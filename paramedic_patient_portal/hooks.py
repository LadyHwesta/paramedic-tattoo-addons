# -*- coding: utf-8 -*-


def post_init_hook(env):
    """Photos already on sessions get their sharing and marketing record
    (not shared, no marketing permission: both are decided afresh)."""
    env["patient.treatment.session"].search([])._sync_patient_photos()
