# -*- coding: utf-8 -*-
import base64
import re

from odoo.exceptions import UserError, ValidationError
from odoo.tests import HttpCase, tagged

# A 1x1 PNG.
PNG = base64.b64encode(bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d"
    "49444154789c6360000002000154a24f5d0000000049454e44ae426082"))


@tagged("post_install", "-at_install")
class TestPatientPortal(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        portal = cls.env.ref("base.group_portal")
        cls.patient_user = cls.env["res.users"].create({
            "name": "Pat Doe", "login": "pat_doe", "password": "pat_doe_pw12",
            "email": "pat@example.com", "group_ids": [(6, 0, [portal.id])]})
        cls.patient = cls.patient_user.partner_id
        cls.patient.is_patient = True
        cls.other_user = cls.env["res.users"].create({
            "name": "Other Patient", "login": "other_pt", "password": "other_pt_pw12",
            "email": "other@example.com", "group_ids": [(6, 0, [portal.id])]})
        cls.other_user.partner_id.is_patient = True
        cls.condition = cls.env["patient.condition"].create({
            "partner_id": cls.patient.id, "condition_type": "scar_camouflage", "area": "Left forearm"})
        cls.before = cls.env["ir.attachment"].create({
            "name": "before.png", "datas": PNG, "mimetype": "image/png"})
        cls.after = cls.env["ir.attachment"].create({
            "name": "after.png", "datas": PNG, "mimetype": "image/png"})
        cls.treatment = cls.env["patient.treatment.session"].create({
            "condition_id": cls.condition.id,
            "before_photo_ids": [(6, 0, [cls.before.id])],
            "after_photo_ids": [(6, 0, [cls.after.id])]})

    def _photo(self, attachment):
        return self.treatment.photo_ids.filtered(lambda p: p.attachment_id == attachment)

    def _note(self, **values):
        return self.env["patient.clinical.note"].create({
            "partner_id": self.patient.id, "title": "Two-week healing check",
            "body": "<p>Healing well; light flaking.</p>", **values})

    # -- notes ---------------------------------------------------------------

    def test_a_note_is_internal_unless_shared(self):
        note = self._note()
        self.assertEqual(note.visibility, "internal")
        self.assertFalse(note.shared_on)

    def test_sharing_a_note_emails_a_link_never_the_note(self):
        mails = self.env["mail.mail"].search([])
        note = self._note()
        note.visibility = "patient"
        self.assertTrue(note.shared_on)
        new = self.env["mail.mail"].search([]) - mails
        self.assertEqual(len(new), 1)
        self.assertIn("/my/records", new.body_html)
        self.assertNotIn("flaking", new.body_html)
        self.assertNotIn("healing", (new.subject or "").lower())

    def test_a_note_cant_point_at_another_patients_session(self):
        other_condition = self.env["patient.condition"].create({
            "partner_id": self.other_user.partner_id.id, "condition_type": "other"})
        other_session = self.env["patient.treatment.session"].create({
            "condition_id": other_condition.id})
        with self.assertRaises(ValidationError):
            self._note(session_id=other_session.id)

    # -- photos ----------------------------------------------------------------

    def test_session_photos_get_a_sharing_record_each(self):
        self.assertEqual(sorted(self.treatment.photo_ids.mapped("kind")), ["after", "before"])
        self.assertFalse(any(self.treatment.photo_ids.mapped("shared_with_patient")))
        self.treatment.before_photo_ids = [(5, 0, 0)]
        self.assertEqual(self.treatment.photo_ids.mapped("kind"), ["after"])

    def test_staff_cant_set_marketing_permission_by_hand(self):
        with self.assertRaises(UserError):
            self._photo(self.after).marketing_ok = True

    def test_a_signed_photo_release_grants_permission(self):
        photo = self._photo(self.after)
        unsigned = self.env["patient.consent"].create({
            "partner_id": self.patient.id, "condition_id": self.condition.id,
            "consent_type": "photo_release"})
        photo.marketing_consent_id = unsigned
        self.assertFalse(photo.marketing_ok, "an unsigned release proves nothing")
        unsigned.signed = True
        photo.marketing_consent_id = False
        photo.marketing_consent_id = unsigned
        self.assertTrue(photo.marketing_ok)
        self.assertEqual(photo.marketing_source, "signed_form")
        self.assertIn("Signed photo release", photo.marketing_label)
        photo.marketing_consent_id = False
        self.assertFalse(photo.marketing_ok)

    # -- the portal --------------------------------------------------------------

    def test_the_portal_shows_only_shared_notes_and_photos(self):
        self._note(title="Internal plan for next session")
        self._note(title="Aftercare reminder", visibility="patient")
        self._photo(self.after).shared_with_patient = True
        self.authenticate("pat_doe", "pat_doe_pw12")
        page = self.url_open("/my/records").text
        self.assertIn("Aftercare reminder", page)
        self.assertNotIn("Internal plan", page)
        self.assertIn(f"/my/records/photo/{self._photo(self.after).id}", page)
        self.assertNotIn(f"/my/records/photo/{self._photo(self.before).id}", page)

    def test_a_photo_is_served_only_to_its_patient_and_only_when_shared(self):
        shared, unshared = self._photo(self.after), self._photo(self.before)
        shared.shared_with_patient = True
        self.authenticate("pat_doe", "pat_doe_pw12")
        response = self.url_open(f"/my/records/photo/{shared.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "image/png")
        self.assertEqual(self.url_open(f"/my/records/photo/{unshared.id}").status_code, 404)
        self.authenticate("other_pt", "other_pt_pw12")
        self.assertEqual(self.url_open(f"/my/records/photo/{shared.id}").status_code, 404)

    def test_the_patient_grants_and_withdraws_marketing_permission(self):
        photo = self._photo(self.after)
        photo.shared_with_patient = True
        self.authenticate("pat_doe", "pat_doe_pw12")
        page = self.url_open("/my/records").text
        token = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)
        self.url_open(f"/my/records/photo/{photo.id}/marketing",
                      data={"allow": "1", "csrf_token": token})
        self.assertTrue(photo.marketing_ok)
        self.assertEqual(photo.marketing_source, "patient")
        self.assertTrue(photo.marketing_date)
        self.assertEqual(self.patient.marketing_photo_count, 1)
        self.url_open(f"/my/records/photo/{photo.id}/marketing",
                      data={"allow": "0", "csrf_token": token})
        self.assertFalse(photo.marketing_ok)
        log = " ".join(photo.message_ids.mapped("body"))
        self.assertIn("allowed", log)
        self.assertIn("withdrew", log)

    def test_another_patient_cant_change_my_photo(self):
        photo = self._photo(self.after)
        photo.shared_with_patient = True
        self.authenticate("other_pt", "other_pt_pw12")
        page = self.url_open("/my").text
        token = re.search(r'csrf_token["\']?\s*[:=]\s*["\']([^"\']+)', page)
        response = self.url_open(f"/my/records/photo/{photo.id}/marketing",
                                 data={"allow": "1", "csrf_token": token.group(1) if token else ""})
        self.assertIn(response.status_code, (400, 404))
        self.assertFalse(photo.marketing_ok)


@tagged("post_install", "-at_install")
class TestOneReleaseManyPhotos(TestPatientPortal):
    """One signed release for many photos: several at once, or all of them."""

    def _release(self, **values):
        return self.env["patient.consent"].create({
            "partner_id": self.patient.id, "condition_id": self.condition.id,
            "consent_type": "photo_release", "signed": True, **values})

    def _second_session(self):
        extra = self.env["ir.attachment"].create({
            "name": "later.png", "datas": PNG, "mimetype": "image/png"})
        return self.env["patient.treatment.session"].create({
            "condition_id": self.condition.id, "after_photo_ids": [(6, 0, [extra.id])]})

    def test_a_release_covering_all_photos_covers_new_ones_too(self):
        release = self._release(covers_all_photos=True)
        self.assertTrue(all(self.treatment.photo_ids.mapped("marketing_ok")))
        later = self._second_session()
        self.assertTrue(later.photo_ids.marketing_ok)
        self.assertEqual(later.photo_ids.marketing_consent_id, release)
        self.assertEqual(release.photo_count, 3)

    def test_a_patients_withdrawal_beats_a_release_covering_everything(self):
        release = self._release(covers_all_photos=True)
        photo = self._photo(self.after)
        photo.shared_with_patient = True
        self.assertTrue(photo.marketing_ok)
        photo._portal_set_marketing(False)  # the patient withdraws this one
        self.assertTrue(photo.withdrawn_by_patient)
        release.signed = False  # e.g. re-signed after a correction
        release.signed = True
        self._release(covers_all_photos=True)  # or a new release later
        self.assertFalse(photo.marketing_ok, "a release must not override the patient")
        self.assertTrue(self._photo(self.before).marketing_ok)
        photo._portal_set_marketing(True)  # only the patient can undo it
        self.assertTrue(photo.marketing_ok)
        self.assertFalse(photo.withdrawn_by_patient)

    def test_unsigning_or_deleting_the_release_ends_its_permission(self):
        release = self._release(covers_all_photos=True)
        release.signed = False
        self.assertFalse(any(self.treatment.photo_ids.mapped("marketing_ok")))
        release.signed = True
        self.assertTrue(all(self.treatment.photo_ids.mapped("marketing_ok")))
        release.unlink()
        self.assertFalse(any(self.treatment.photo_ids.mapped("marketing_ok")))

    def test_attach_one_release_to_several_photos_at_once(self):
        release = self._release()
        photos = self.treatment.photo_ids
        wizard = self.env["patient.photo.release.wizard"].with_context(
            active_ids=photos.ids).create({"consent_id": release.id})
        self.assertEqual(wizard.partner_id, self.patient)
        wizard.action_attach()
        self.assertTrue(all(photos.mapped("marketing_ok")))
        self.assertEqual(set(photos.mapped("marketing_source")), {"signed_form"})

    def test_several_patients_photos_cant_share_a_release(self):
        other_condition = self.env["patient.condition"].create({
            "partner_id": self.other_user.partner_id.id, "condition_type": "other"})
        other_photo_file = self.env["ir.attachment"].create({
            "name": "o.png", "datas": PNG, "mimetype": "image/png"})
        other = self.env["patient.treatment.session"].create({
            "condition_id": other_condition.id, "after_photo_ids": [(6, 0, [other_photo_file.id])]})
        with self.assertRaises(UserError):
            self.env["patient.photo.release.wizard"].with_context(
                active_ids=(self.treatment.photo_ids | other.photo_ids).ids).create({})
