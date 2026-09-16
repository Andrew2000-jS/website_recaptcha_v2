from unittest.mock import Mock, patch

from odoo.tests import TransactionCase

from odoo.addons.website_recaptcha_v2.controllers.website import WebsiteRecaptchaForm
from odoo.addons.website_recaptcha_v2.models.ir_http import _VERIFY_URL


class TestWebsiteRecaptchaV2(TransactionCase):
    def setUp(self):
        super().setUp()
        self.config = self.env["ir.config_parameter"].sudo()
        self.config.set_param("website_recaptcha_v2.enabled", "True")
        self.config.set_param("website_recaptcha_v2.site_key", "site-key-placeholder")
        self.config.set_param("website_recaptcha_v2.secret_key", "secret-key-placeholder")

    def test_settings_parameters_are_isolated(self):
        settings = self.env["res.config.settings"].create({
            "website_recaptcha_v2_enabled": True,
            "website_recaptcha_v2_site_key": "new-site-key",
            "website_recaptcha_v2_secret_key": "new-secret-key",
            "website_recaptcha_v2_failure_message": "Custom failure",
        })
        settings.execute()
        self.assertEqual(self.config.get_param("website_recaptcha_v2.site_key"), "new-site-key")
        self.assertEqual(self.config.get_param("recaptcha_public_key"), False)

    def test_verification_success(self):
        response = Mock(status_code=200)
        response.json.return_value = {"success": True, "hostname": "localhost"}
        with patch("requests.post", return_value=response) as post:
            self.assertTrue(
                self.env["ir.http"]._verify_website_recaptcha_v2_token("token")
            )
        self.assertEqual(post.call_args.args[0], _VERIFY_URL)

    def test_verification_failure_malformed_and_timeout_fail_closed(self):
        for result in ({"success": False}, {}, {"success": True, "hostname": "other.example"}):
            response = Mock(status_code=200)
            response.json.return_value = result
            with patch("requests.post", return_value=response):
                self.assertFalse(
                    self.env["ir.http"]._verify_website_recaptcha_v2_token("token")
                )

        import requests

        with patch("requests.post", side_effect=requests.exceptions.Timeout):
            self.assertFalse(
                self.env["ir.http"]._verify_website_recaptcha_v2_token("token")
            )

    def test_missing_token_is_rejected_when_enabled(self):
        self.assertFalse(self.env["ir.http"]._verify_website_recaptcha_v2_token())

    def test_public_templates_contain_one_checkbox_container(self):
        for template_name, form_class in (
            ("web.login", "oe_login_form"),
            ("auth_signup.signup", "oe_signup_form"),
            ("auth_signup.reset_password", "oe_reset_password_form"),
        ):
            with self.subTest(template_name=template_name):
                arch = self.env["ir.ui.view"]._render_template(template_name, {})
                self.assertEqual(
                    str(arch).count("data-website-recaptcha-v2-widget"), 1,
                    form_class,
                )

    def test_generic_route_rejects_missing_token_and_accepts_verified_token(self):
        ir_http = self.env["ir.http"]
        fake_request = Mock()
        fake_request.env = {"ir.http": ir_http}
        with patch(
            "odoo.addons.website_recaptcha_v2.controllers.website.request",
            fake_request,
        ), patch.object(
            ir_http, "_verify_website_recaptcha_v2_token", return_value=False
        ):
            result = WebsiteRecaptchaForm().website_form("res.partner")
        self.assertIn("error", result)

        with patch(
            "odoo.addons.website_recaptcha_v2.controllers.website.request",
            fake_request,
        ), patch.object(
            ir_http, "_verify_website_recaptcha_v2_token", return_value=True
        ), patch(
            "odoo.addons.website.controllers.form.WebsiteForm.website_form",
            return_value="accepted",
        ):
            self.assertEqual(WebsiteRecaptchaForm().website_form("res.partner"), "accepted")
