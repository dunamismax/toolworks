from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "work_emailer.py"
SPEC = importlib.util.spec_from_file_location("work_emailer", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_build_greeting_prefers_custom_greeting():
    greeting = MODULE.build_greeting(
        name="Stephen",
        company="Imaging Services Inc",
        custom_greeting="Hello Stephen,",
    )
    assert greeting == "Hello Stephen,"


def test_build_greeting_uses_name_then_company_then_generic():
    assert MODULE.build_greeting(name="Stephen") == "Hello Stephen,"
    assert (
        MODULE.build_greeting(company="Atlas Animal Hospital")
        == "Hello Atlas Animal Hospital team,"
    )
    assert MODULE.build_greeting() == "Hello,"


def test_build_email_request_uses_template_subject_and_cc_defaults():
    email = MODULE.build_email_request(
        template_key="tailscale",
        recipient="stephen@example.com",
        name="Stephen",
    )
    assert email.subject == "Secure remote X-Ray access with Tailscale"
    assert email.cc_email == MODULE.DEFAULT_CC_EMAIL
    assert "Hello Stephen," in email.html_body
    assert email.template.template_file == "tailscale-remote-access.html"


def test_build_email_request_supports_subject_override_and_no_cc():
    email = MODULE.build_email_request(
        template_key="cloudbackup",
        recipient="stephen@example.com",
        company="Atlas Animal Hospital",
        cc_email=None,
        subject_override="Custom subject",
    )
    assert email.subject == "Custom subject"
    assert email.cc_email is None
    assert "Hello Atlas Animal Hospital team," in email.html_body


def test_parse_args_selects_requested_template_and_recipient():
    args = MODULE.parse_args(["--coverage150credit", "stephen@example.com", "--name", "Stephen"])
    assert args.template_key == "coverage150credit"
    assert args.recipient == "stephen@example.com"
    assert args.name == "Stephen"


def test_render_template_replaces_greeting_placeholder():
    spec = MODULE.TEMPLATE_SPECS["windows10upgrade"]
    rendered = MODULE.render_template(spec, "Hello Stephen,")
    assert "Hello Stephen," in rendered
    assert "{{GREETING}}" not in rendered


def test_parse_args_allows_template_listing_without_recipient():
    args = MODULE.parse_args(["--list-templates"])
    assert args.list_templates is True
