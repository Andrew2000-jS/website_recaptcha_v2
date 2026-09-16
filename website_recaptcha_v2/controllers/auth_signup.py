import werkzeug

from odoo import http
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.home import SIGN_UP_REQUEST_PARAMS, ensure_db
from odoo.http import request


class WebsiteRecaptchaAuthSignup(AuthSignupHome):
    def _website_recaptcha_v2_error_response(self, template, qcontext):
        qcontext["error"] = request.env["ir.http"]._website_recaptcha_v2_failure_message()
        response = request.render(template, qcontext)
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response

    @http.route()
    def web_login(self, *args, **kw):
        # Reject credentials before the inherited controller can authenticate
        # them. A successful signup calls this method again after authentication,
        # so do not require a second, already-consumed v2 token in that case.
        ensure_db()
        if (
            request.httprequest.method == "POST"
            and not request.session.uid
            and not request.env["ir.http"]._verify_website_recaptcha_v2_token(
                kw.get("g-recaptcha-response")
            )
        ):
            qcontext = {
                key: value
                for key, value in request.params.items()
                if key in SIGN_UP_REQUEST_PARAMS
            }
            qcontext.update(self.get_auth_signup_config())
            qcontext.update(
                {
                    "login": kw.get("login"),
                    "error": request.env[
                        "ir.http"
                    ]._website_recaptcha_v2_failure_message(),
                }
            )
            response = request.render("web.login", qcontext)
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
            response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
            return response
        return super().web_login(*args, **kw)

    @http.route()
    def web_auth_signup(self, *args, **kw):
        if request.httprequest.method == "POST" and not request.env[
            "ir.http"
        ]._verify_website_recaptcha_v2_token(kw.get("g-recaptcha-response")):
            qcontext = self.get_auth_signup_qcontext()
            if not qcontext.get("token") and not qcontext.get("signup_enabled"):
                raise werkzeug.exceptions.NotFound()
            return self._website_recaptcha_v2_error_response("auth_signup.signup", qcontext)
        return super().web_auth_signup(*args, **kw)

    @http.route()
    def web_auth_reset_password(self, *args, **kw):
        if request.httprequest.method == "POST" and not request.env[
            "ir.http"
        ]._verify_website_recaptcha_v2_token(kw.get("g-recaptcha-response")):
            qcontext = self.get_auth_signup_qcontext()
            if not qcontext.get("token") and not qcontext.get("reset_password_enabled"):
                raise werkzeug.exceptions.NotFound()
            return self._website_recaptcha_v2_error_response(
                "auth_signup.reset_password", qcontext
            )
        return super().web_auth_reset_password(*args, **kw)
