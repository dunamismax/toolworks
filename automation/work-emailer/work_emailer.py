#!/usr/bin/env python3
"""Send post-call follow-up email templates through Outlook on macOS."""

from __future__ import annotations

import argparse
import platform
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CC_EMAIL = "support@imagingservices.net"
TEMPLATE_DIR = Path(__file__).parent / "templates"


@dataclass(frozen=True)
class TemplateSpec:
    key: str
    flag: str
    subject: str
    template_file: str
    description: str

    @property
    def path(self) -> Path:
        return TEMPLATE_DIR / self.template_file


TEMPLATE_SPECS = {
    "tailscale": TemplateSpec(
        key="tailscale",
        flag="--tailscale",
        subject="Secure remote X-Ray access with Tailscale",
        template_file="tailscale-remote-access.html",
        description="Remote imaging access follow-up",
    ),
    "windows10upgrade": TemplateSpec(
        key="windows10upgrade",
        flag="--windows10upgrade",
        subject="Windows 10 upgrade paths for your X-Ray PC",
        template_file="windows-10-upgrade.html",
        description="Windows lifecycle and upgrade options",
    ),
    "cloudbackup": TemplateSpec(
        key="cloudbackup",
        flag="--cloudbackup",
        subject="Cloud backup and disaster recovery for your X-Ray system",
        template_file="cloud-backup-only.html",
        description="Cloud backup only offer",
    ),
    "coverage150credit": TemplateSpec(
        key="coverage150credit",
        flag="--coverage150credit",
        subject="Comprehensive coverage follow-up with your $150 credit",
        template_file="coverage-150-credit.html",
        description="Support package with $150 credit",
    ),
    "coverage300credit": TemplateSpec(
        key="coverage300credit",
        flag="--coverage300credit",
        subject="Comprehensive coverage follow-up with your $300 credit",
        template_file="coverage-300-credit.html",
        description="Support package with $300 credit",
    ),
}


@dataclass(frozen=True)
class RenderedEmail:
    recipient: str
    cc_email: str | None
    subject: str
    greeting: str
    html_body: str
    template: TemplateSpec


def build_greeting(
    *,
    name: str | None = None,
    company: str | None = None,
    custom_greeting: str | None = None,
) -> str:
    if custom_greeting:
        return custom_greeting.strip()
    if name and name.strip():
        return f"Hello {name.strip()},"
    if company and company.strip():
        return f"Hello {company.strip()} team,"
    return "Hello,"


def load_template(spec: TemplateSpec) -> str:
    return spec.path.read_text(encoding="utf-8")


def render_template(spec: TemplateSpec, greeting: str) -> str:
    html = load_template(spec)
    return html.replace("{{GREETING}}", greeting)


def build_email_request(
    *,
    template_key: str,
    recipient: str,
    name: str | None = None,
    company: str | None = None,
    custom_greeting: str | None = None,
    cc_email: str | None = DEFAULT_CC_EMAIL,
    subject_override: str | None = None,
) -> RenderedEmail:
    spec = TEMPLATE_SPECS[template_key]
    greeting = build_greeting(name=name, company=company, custom_greeting=custom_greeting)
    subject = subject_override.strip() if subject_override else spec.subject
    return RenderedEmail(
        recipient=recipient,
        cc_email=cc_email,
        subject=subject,
        greeting=greeting,
        html_body=render_template(spec, greeting),
        template=spec,
    )


def applescript_quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def send_html_via_outlook(
    *,
    to_email: str,
    subject: str,
    html_body: str,
    cc_email: str | None = None,
) -> bool:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".html",
        delete=False,
        encoding="utf-8",
    ) as handle:
        handle.write(html_body)
        html_path = handle.name

    quoted_path = applescript_quote(html_path)
    quoted_subject = applescript_quote(subject)
    quoted_to_email = applescript_quote(to_email)

    if cc_email:
        cc_line = (
            "make new cc recipient at newMessage with properties "
            f'{{email address:{{address:"{applescript_quote(cc_email)}"}}}}'
        )
    else:
        cc_line = ""

    message_line = (
        'set newMessage to make new outgoing message with properties '
        f'{{subject:"{quoted_subject}", content:htmlContent}}'
    )
    recipient_line = (
        'make new to recipient at newMessage with properties '
        f'{{email address:{{address:"{quoted_to_email}"}}}}'
    )

    script = f'''
    set htmlFile to POSIX file "{quoted_path}"
    set htmlContent to read htmlFile as «class utf8»

    tell application "Microsoft Outlook"
        {message_line}
        {recipient_line}
        {cc_line}
        send newMessage
    end tell
    '''

    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30,
        )
    finally:
        Path(html_path).unlink(missing_ok=True)

    if result.returncode != 0:
        print(f"AppleScript error: {result.stderr.strip()}", file=sys.stderr)
        return False
    return True


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send post-call work email templates via Outlook")
    template_group = parser.add_mutually_exclusive_group()
    for spec in TEMPLATE_SPECS.values():
        template_group.add_argument(
            spec.flag,
            dest="template_key",
            action="store_const",
            const=spec.key,
            help=f"Use the {spec.description.lower()} template",
        )

    parser.add_argument("recipient", nargs="?", help="Recipient email address")
    parser.add_argument("--name", help="Recipient name for the greeting")
    parser.add_argument("--company", help="Company name for the greeting")
    parser.add_argument("--greeting", help="Explicit greeting line override")
    parser.add_argument(
        "--cc",
        default=DEFAULT_CC_EMAIL,
        help="CC address (default: support inbox)",
    )
    parser.add_argument("--no-cc", action="store_true", help="Do not CC anyone")
    parser.add_argument(
        "--subject",
        help="Override the default subject for the selected template",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available templates and exit",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.list_templates:
        return args

    if not args.template_key:
        parser.error("select exactly one template flag")
    if not args.recipient:
        parser.error("recipient email address is required")

    return args


def print_template_list() -> None:
    print("Available templates:")
    for spec in TEMPLATE_SPECS.values():
        print(f"  {spec.flag:<20} {spec.subject}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.list_templates:
        print_template_list()
        return 0

    cc_email = None if args.no_cc else args.cc
    email = build_email_request(
        template_key=args.template_key,
        recipient=args.recipient,
        name=args.name,
        company=args.company,
        custom_greeting=args.greeting,
        cc_email=cc_email,
        subject_override=args.subject,
    )

    print(f"Template: {email.template.key}")
    print(f"To: {email.recipient}")
    print(f"CC: {email.cc_email or '(none)'}")
    print(f"Subject: {email.subject}")
    print(f"Greeting: {email.greeting}")

    if args.dry_run:
        print("Dry run only. Email was not sent.")
        return 0

    if platform.system() != "Darwin":
        print("This sender only supports macOS Outlook.", file=sys.stderr)
        return 1

    success = send_html_via_outlook(
        to_email=email.recipient,
        subject=email.subject,
        html_body=email.html_body,
        cc_email=email.cc_email,
    )
    if not success:
        return 1

    print("Email sent successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
