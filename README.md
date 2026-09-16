# Website Google reCAPTCHA v2 Checkbox

This standalone Odoo 18 addon protects supported public website submissions with Google's legacy reCAPTCHA v2 checkbox. It does not contain or depend on Singer business logic.

## Author and license

Developed by [Andrés Arévalo](https://github.com/Andrew2000-jS).

This module is proprietary software. All rights are reserved. See [LICENSE](LICENSE) for the applicable terms.

## Installation

1. Add `website_recaptcha_v2` to the Odoo addons path.
2. Update the Apps list and install **Website Google reCAPTCHA v2 Checkbox**.
3. Upgrade the module after changing its files or after an Odoo upgrade.

The addon requires `website` and `website_sale` so it can protect generic website forms and checkout address submissions. `auth_signup` and `website_mass_mailing` are not hard dependencies.

## Configuration

Open **Settings > Website reCAPTCHA v2** and enable protection. Enter the public site key and the server-only secret key.

Create the Google key as **Challenge (Prueba) (v2) checkbox**, not **Score (v3)**. Register every public hostname that serves the site, including staging domains when needed. Use placeholders such as `SITE_KEY_PLACEHOLDER` and `SECRET_KEY_PLACEHOLDER` in documentation or configuration examples; never commit real keys.

The secret key is stored in an Odoo configuration parameter and is never rendered into frontend HTML. The configured failure message is shown when the checkbox is incomplete or Google verification fails.

The module uses these dedicated parameters:

- `website_recaptcha_v2.enabled`
- `website_recaptcha_v2.site_key`
- `website_recaptcha_v2.secret_key`
- `website_recaptcha_v2.failure_message`

These are intentionally separate from Odoo's native v3 parameters (`recaptcha_public_key`, `recaptcha_private_key`, and `recaptcha_min_score`). If native `google_recaptcha` is installed, configure both integrations as required by the installed forms; this addon does not convert or disable native v3 behavior.

## Supported surfaces and boundary

- Generic `website` form-builder submissions through `/website/form/<model_name>`.
- `website_sale` checkout address submissions through `/shop/address/submit`.
- Signup and password reset forms when `auth_signup` is installed. Their Python controller extension is conditional, and the frontend widget is attached by selector.

The visible checkbox is added to supported QWeb forms and discovered on dynamically inserted supported forms. It uses Google's responsive widget and a small mobile adjustment. Client-side blocking is only a usability feature; every supported route verifies the token server-side and fails closed when protection is enabled.

Newsletter routes from `website_mass_mailing`, arbitrary custom controllers, JSON endpoints, payment forms, and unrelated third-party forms are not universally intercepted. Protect those endpoints through their own server-side extension point before enabling this addon for them. Extending `ir.http` globally would risk changing route semantics and is deliberately avoided.

## Security

Do not expose the secret key, put it in JavaScript, log it, or commit it. Google receives the visitor token and request IP during verification. Keep Google hostname configuration aligned with Odoo's public host and review proxy configuration so hostname validation is meaningful. Network errors, malformed responses, invalid tokens, missing keys, and hostname mismatches are rejected.

## Upgrade

Back up the database, update the addon files, restart Odoo using the normal deployment process, and install or upgrade the module (`-i website_recaptcha_v2` or `-u website_recaptcha_v2`) in the target database. Recheck the configuration after upgrades and verify each supported form with a real v2 checkbox key.
