/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { loadJS } from "@web/core/assets";

const FORM_SELECTOR = "form";

let apiPromise;

function hasExplicitRender(api) {
    return typeof api?.render === "function";
}

function configuration() {
    const meta = document.querySelector("meta[name='website-recaptcha-v2']");
    return meta && {
        siteKey: meta.content,
        errorMessage: meta.dataset.errorMessage || _t("Please complete the reCAPTCHA challenge and try again."),
    };
}

function loadApi() {
    const existingApi = window.grecaptcha;
    if (hasExplicitRender(existingApi)) {
        return Promise.resolve(existingApi);
    }
    if (!apiPromise) {
        const callbackName = "__websiteRecaptchaV2Loaded";
        apiPromise = new Promise((resolve, reject) => {
            const cleanup = () => {
                delete window[callbackName];
            };
            window[callbackName] = () => {
                const v2Api = window.grecaptcha;
                if (!hasExplicitRender(v2Api)) {
                    cleanup();
                    reject(new Error("Google reCAPTCHA API loaded without grecaptcha.render"));
                    return;
                }
                // Keep Odoo's v3 API global intact while retaining the v2 API reference.
                if (existingApi && existingApi !== v2Api) {
                    window.grecaptcha = existingApi;
                }
                cleanup();
                resolve(v2Api);
            };
            loadJS(
                `https://www.recaptcha.net/recaptcha/api.js?onload=${callbackName}&render=explicit`,
            ).catch((error) => {
                cleanup();
                reject(error);
            });
        });
    }
    return apiPromise;
}

function setError(form, message) {
    let error = form.querySelector(".website-recaptcha-v2-error");
    if (!error) {
        error = document.createElement("div");
        error.className = "alert alert-danger website-recaptcha-v2-error";
        error.setAttribute("role", "alert");
        const widget = form.querySelector("[data-website-recaptcha-v2-widget]");
        (widget || form).append(error);
    }
    error.textContent = message;
    error.classList.remove("d-none");
}

function clearError(form) {
    form.querySelector(".website-recaptcha-v2-error")?.classList.add("d-none");
}

function placeAfterSubmit(form, container) {
    const submitBlock = form.querySelector(".s_website_form_submit, .oe_login_buttons");
    if (submitBlock) {
        submitBlock.insertAdjacentElement("afterend", container);
        return;
    }
    const submitControl = form.querySelector(
        "button[type='submit'], input[type='submit'], .s_website_form_send, .o_website_form_send",
    );
    if (submitControl) {
        submitControl.insertAdjacentElement("afterend", container);
        return;
    }
    form.append(container);
}

function render(form) {
    const config = configuration();
    if (!config) {
        return;
    }
    let container = form.querySelector("[data-website-recaptcha-v2-widget]");
    if (!container) {
        container = document.createElement("div");
        container.className = "website-recaptcha-v2-container";
        container.dataset.websiteRecaptchaV2Widget = "1";
        placeAfterSubmit(form, container);
    } else {
        placeAfterSubmit(form, container);
    }
    if (container.dataset.websiteRecaptchaV2State) {
        return;
    }
    container.dataset.websiteRecaptchaV2State = "loading";
    if (!config.siteKey) {
        container.dataset.websiteRecaptchaV2State = "failed";
        console.error("Website reCAPTCHA v2 cannot render: site key is not configured");
        setError(form, config.errorMessage);
        return;
    }
    loadApi().then((grecaptcha) => new Promise((resolve, reject) => {
        grecaptcha.ready(() => {
            try {
                grecaptcha.render(container, {
                    sitekey: config.siteKey,
                    callback: () => clearError(form),
                    "expired-callback": () => {
                        const token = form.querySelector("textarea[name='g-recaptcha-response']");
                        if (token) token.value = "";
                    },
                    "error-callback": () => setError(form, config.errorMessage),
                });
                resolve();
            } catch (error) {
                reject(error);
            }
        });
    })).then(() => {
        container.dataset.websiteRecaptchaV2State = "rendered";
    }).catch((error) => {
        container.dataset.websiteRecaptchaV2State = "failed";
        console.error("Website reCAPTCHA v2 failed to load or render", error);
        setError(form, config.errorMessage);
    });
}

function isProtectedForm(form) {
    if (form.matches("[data-website-recaptcha-v2-form], .oe_login_form, .oe_signup_form, .oe_reset_password_form")) {
        return true;
    }
    const action = form.getAttribute("action");
    if (!action) {
        return false;
    }
    try {
        const pathname = new URL(action, window.location.href).pathname.replace(/\/$/, "");
        return (
            pathname === "/website/form"
            || pathname.startsWith("/website/form/")
            || pathname === "/shop/address/submit"
        );
    } catch (error) {
        console.error("Website reCAPTCHA v2 ignored an invalid form action", error);
        return false;
    }
}

function protectedForm(target) {
    const form = target instanceof HTMLFormElement ? target : target.closest?.(FORM_SELECTOR);
    return form && isProtectedForm(form) ? form : null;
}

document.addEventListener("click", (event) => {
    const form = protectedForm(event.target);
    if (!form || !event.target.closest("button[type='submit'], input[type='submit'], .s_website_form_send, .o_website_form_send")) {
        return;
    }
    const token = form.querySelector("textarea[name='g-recaptcha-response']")?.value;
    if (!token) {
        event.preventDefault();
        event.stopImmediatePropagation();
        setError(form, configuration()?.errorMessage || _t("Please complete the reCAPTCHA challenge and try again."));
    }
}, true);

document.addEventListener("submit", (event) => {
    const form = protectedForm(event.target);
    if (!form) return;
    const token = form.querySelector("textarea[name='g-recaptcha-response']")?.value;
    if (!token) {
        event.preventDefault();
        event.stopImmediatePropagation();
        setError(form, configuration()?.errorMessage || _t("Please complete the reCAPTCHA challenge and try again."));
    }
}, true);

function scan(root = document) {
    root.querySelectorAll?.(FORM_SELECTOR).forEach((form) => {
        if (isProtectedForm(form)) render(form);
    });
    if (root.matches?.(FORM_SELECTOR) && isProtectedForm(root)) render(root);
}

function start() {
    scan();
    new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) scan(node);
            });
        }
    }).observe(document.body, { childList: true, subtree: true });
}

if (document.body) {
    start();
} else {
    document.addEventListener("DOMContentLoaded", start, { once: true });
}
