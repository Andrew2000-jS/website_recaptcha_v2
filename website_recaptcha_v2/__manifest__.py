{
    "name": "Website Google reCAPTCHA v2 Checkbox",
    "summary": "Protect supported public website forms with Google reCAPTCHA v2",
    "version": "18.0.1.0.0",
    "category": "Website/Website",
    "author": "Andrés Arévalo",
    "website": "https://github.com/Andrew2000-jS",
    "license": "Other proprietary",
    "depends": ["website", "website_sale", "google_recaptcha"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/website_recaptcha_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            (
                "before",
                "google_recaptcha/static/src/js/recaptcha.js",
                "website_recaptcha_v2/static/src/js/recaptcha.js",
            ),
            "website_recaptcha_v2/static/src/scss/recaptcha.scss",
        ],
    },
    "installable": True,
    "application": False,
}
