"""Transactional email via Resend (https://resend.com). Requires the
RESEND_API_KEY environment variable; without it, sends are skipped with a
warning logged to stdout so local development doesn't need a real account.
"""

import os

import requests

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "Simulateur ETF <no-reply@sortino.fr>")
APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8000").rstrip("/")

_BUTTON_STYLE = (
    "display:inline-block; padding:12px 22px; background:#0b0b0b; color:#ffffff; "
    "font-family:sans-serif; font-weight:600; text-decoration:none; border-radius:8px;"
)
_WRAP_STYLE = "font-family:sans-serif; color:#0b0b0b; max-width:480px; margin:0 auto; line-height:1.5;"


def _send(to: str, subject: str, html: str) -> bool:
    if not RESEND_API_KEY:
        print(f"WARNING: RESEND_API_KEY not set — skipping email to {to} ({subject!r}).")
        return False
    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json={"from": EMAIL_FROM, "to": [to], "subject": subject, "html": html},
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:
        print(f"ERROR: failed to send email to {to} ({subject!r}): {exc}")
        return False


def send_verification_email(to: str, token: str) -> bool:
    link = f"{APP_BASE_URL}/?verify_token={token}"
    html = f"""
    <div style="{_WRAP_STYLE}">
      <h2>Vérifiez votre adresse email</h2>
      <p>Confirmez votre adresse pour activer pleinement votre compte sur le Simulateur de portefeuille ETF.</p>
      <p><a href="{link}" style="{_BUTTON_STYLE}">Vérifier mon email</a></p>
      <p style="color:#6b6a65; font-size:13px;">Ce lien expire dans 48 heures. Si vous n'êtes pas à l'origine de cette
      inscription, ignorez simplement cet email.</p>
    </div>
    """
    return _send(to, "Vérifiez votre adresse email", html)


def send_reset_email(to: str, token: str) -> bool:
    link = f"{APP_BASE_URL}/?reset_token={token}"
    html = f"""
    <div style="{_WRAP_STYLE}">
      <h2>Réinitialisation de votre mot de passe</h2>
      <p>Une demande de réinitialisation de mot de passe a été faite pour ce compte.</p>
      <p><a href="{link}" style="{_BUTTON_STYLE}">Choisir un nouveau mot de passe</a></p>
      <p style="color:#6b6a65; font-size:13px;">Ce lien expire dans 1 heure. Si vous n'êtes pas à l'origine de cette
      demande, ignorez simplement cet email — votre mot de passe actuel reste inchangé.</p>
    </div>
    """
    return _send(to, "Réinitialisation de votre mot de passe", html)
