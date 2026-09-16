import json

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteRecaptchaSale(WebsiteSale):
    @http.route()
    def shop_address_submit(self, *args, **kwargs):
        if not request.env["ir.http"]._verify_website_recaptcha_v2_token(
            kwargs.get("g-recaptcha-response")
        ):
            return json.dumps({
                "invalid_fields": [],
                "messages": [
                    request.env["ir.http"]
                    ._website_recaptcha_v2_failure_message()
                ],
            })
        return super().shop_address_submit(*args, **kwargs)
