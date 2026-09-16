import json

from odoo import http
from odoo.addons.website.controllers.form import WebsiteForm
from odoo.http import request


class WebsiteRecaptchaForm(WebsiteForm):
    @http.route()
    def website_form(self, model_name, **kwargs):
        if not request.env["ir.http"]._verify_website_recaptcha_v2_token(
            kwargs.get("g-recaptcha-response")
        ):
            return json.dumps({
                "error": request.env["ir.http"]
                ._website_recaptcha_v2_failure_message(),
            })
        return super().website_form(model_name, **kwargs)
