from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    website_recaptcha_v2_enabled = fields.Boolean(
        "Enable Google reCAPTCHA v2",
        config_parameter="website_recaptcha_v2.enabled",
        groups="base.group_system",
    )
    website_recaptcha_v2_site_key = fields.Char(
        "Site Key",
        config_parameter="website_recaptcha_v2.site_key",
        groups="base.group_system",
    )
    website_recaptcha_v2_secret_key = fields.Char(
        "Secret Key",
        config_parameter="website_recaptcha_v2.secret_key",
        groups="base.group_system",
    )
    website_recaptcha_v2_failure_message = fields.Char(
        "Failure Message",
        config_parameter="website_recaptcha_v2.failure_message",
        default="Please complete the reCAPTCHA challenge and try again.",
        groups="base.group_system",
    )
