import logging
from urllib.parse import urlsplit

import requests

from odoo import api, models
from odoo.http import request

_logger = logging.getLogger(__name__)
_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
_TIMEOUT = 3


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @api.model
    def _website_recaptcha_v2_enabled(self):
        enabled = self.env["ir.config_parameter"].sudo().get_param(
            "website_recaptcha_v2.enabled", "False"
        )
        return str(enabled).lower() in ("1", "true", "yes")

    @api.model
    def _website_recaptcha_v2_failure_message(self):
        return self.env["ir.config_parameter"].sudo().get_param(
            "website_recaptcha_v2.failure_message",
            "Please complete the reCAPTCHA challenge and try again.",
        )

    @api.model
    def _verify_website_recaptcha_v2_token(self, token=None):
        """Return whether the current request has a valid v2 checkbox token."""
        if not self._website_recaptcha_v2_enabled():
            return True

        config = self.env["ir.config_parameter"].sudo()
        secret = config.get_param("website_recaptcha_v2.secret_key")
        site_key = config.get_param("website_recaptcha_v2.site_key")
        if not token:
            try:
                token = request.params.get("g-recaptcha-response")
            except RuntimeError:
                token = None
        if not secret or not site_key or not token:
            _logger.warning("reCAPTCHA v2 rejected request: incomplete configuration or token")
            return False

        data = {
            "secret": secret,
            "response": token,
        }
        try:
            httprequest = request.httprequest
        except RuntimeError:
            httprequest = None
        remote_ip = httprequest and httprequest.remote_addr
        if remote_ip:
            data["remoteip"] = remote_ip
        try:
            response = requests.post(_VERIFY_URL, data=data, timeout=_TIMEOUT)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.Timeout:
            _logger.warning("reCAPTCHA v2 verification timed out")
            return False
        except (requests.exceptions.RequestException, ValueError, TypeError):
            _logger.warning("reCAPTCHA v2 verification returned an invalid response")
            return False

        if not isinstance(result, dict) or result.get("success") is not True:
            _logger.info(
                "reCAPTCHA v2 verification failed with errors %s",
                result.get("error-codes", []),
            )
            return False

        hostname = result.get("hostname")
        request_hostname = httprequest and urlsplit(httprequest.host_url).hostname
        if isinstance(hostname, str) and request_hostname:
            if hostname.lower().rstrip(".") != request_hostname.lower().rstrip("."):
                _logger.warning("reCAPTCHA v2 verification hostname mismatch")
                return False
        return True
