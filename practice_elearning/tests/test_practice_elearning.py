# -*- coding: utf-8 -*-
import re

from odoo.tests import TransactionCase, tagged
from odoo.tools import file_path


@tagged("post_install", "-at_install")
class TestPracticeElearning(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.staff_group = cls.env.ref("practice_base.group_practice_staff")
        cls.clinical = cls.env.ref("practice_elearning.channel_records")
        cls.scheduling = cls.env.ref("practice_elearning.channel_scheduling")

    def _assert_course(self, channel, section_count, lesson_count):
        self.assertTrue(channel.is_published)
        self.assertEqual(channel.visibility, "members")
        self.assertEqual(channel.enroll, "invite")
        self.assertIn(self.staff_group, channel.enroll_group_ids)

        sections = channel.slide_ids.filtered("is_category")
        self.assertEqual(len(sections), section_count)
        lessons = channel.slide_content_ids.filtered(
            lambda s: s.slide_category == "article")
        self.assertEqual(len(lessons), lesson_count)
        for lesson in lessons:
            self.assertTrue(lesson.category_id, "%s has no section" % lesson.name)

        quiz = channel.slide_content_ids.filtered(
            lambda s: s.slide_category == "quiz")
        self.assertEqual(len(quiz), 1)
        self.assertEqual(len(quiz.question_ids), 4)
        for question in quiz.question_ids:
            self.assertFalse(question.answers_validation_error)
            self.assertEqual(
                len(question.answer_ids.filtered("is_correct")), 1)

    def test_records_course_structure(self):
        self._assert_course(self.clinical, section_count=3, lesson_count=5)

    def test_scheduling_course_structure(self):
        self._assert_course(self.scheduling, section_count=2, lesson_count=4)

    def test_courses_are_distinct(self):
        self.assertNotEqual(self.clinical, self.scheduling)

    def test_screenshots_exist(self):
        found = []
        for channel in (self.clinical, self.scheduling):
            for lesson in channel.slide_content_ids:
                found += re.findall(r'src="/([^"]+\.png)"', lesson.html_content or "")
        self.assertTrue(found)
        for image in found:
            self.assertTrue(file_path(image))

    def test_every_lesson_is_published(self):
        """A lesson starts unpublished, so each one must say so in the data,
        or learners see the course but none of its pages."""
        data = self.env["ir.model.data"].search(
            [("module", "=", "practice_elearning"), ("model", "=", "slide.slide")])
        lessons = self.env["slide.slide"].browse(data.mapped("res_id"))
        self.assertTrue(lessons)
        self.assertFalse(lessons.filtered(lambda s: not s.is_published).mapped("name"))

    def test_data_file_matches_the_generator(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build", file_path("practice_elearning/tools/build_course_data.py"))
        build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build)
        body = "".join(build.course_xml(build.M, c[:5], c[5]) for c in (build.RECORDS, build.SCHEDULING))
        with open(file_path("practice_elearning/data/slide_channel_data.xml")) as f:
            self.assertIn(body, f.read(), "Rebuild: python3 practice_elearning/tools/build_course_data.py")
