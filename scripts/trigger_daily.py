# scripts/trigger_daily.py
# JRAVIS Daily Report Trigger (for Render Cron)
# -------------------------------------------------------
# Calls the backend to generate the daily report, then emails confirmation.
# -------------------------------------------------------

import os
import requests
import smtplib
from email.message import EmailMessage

# ---------------- CONFIG ----------------
BACKEND_URL = "https://jravis-backend.onrender.com/api/send_daily_report?code=2040"
TIMEOUT = 30  # seconds

# Gmail SMTP credentials (set in Render Environment Variables)
GMAIL_USER = os.getenv("GMAIL_USER", "yourgmail@gmail.com")
GMAIL_PASS = os.getenv("GMAIL_APP_PASSWORD")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "nrveeresh327@gmail.com")

# ---------------- FUNCTIONS ----------------
def send_email(subject: str, body: str, to: str):
    """Send an email notification via Gmail SMTP."""
    if not GMAIL_USER or not GMAIL_PASS:
        print("⚠️ Gmail credentials not found. Skipping email.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = to
    msg.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(GMAIL_USER, GMAIL_PASS)
            smtp.send_message(msg)
        print(f"✅ Email sent successfully to {to}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")


def trigger_backend():
    """Trigger JRAVIS backend to generate daily report."""
    print(f"[trigger_daily] Calling {BACKEND_URL}")
    try:
        r = requests.get(BACKEND_URL, timeout=TIMEOUT)
        print(f"[trigger_daily] HTTP {r.status_code} - {r.text[:500]}")

        if r.status_code == 200:
            print("[trigger_daily] SUCCESS ✅")
            send_email(
                subject="JRAVIS Daily Report ✅",
                body="JRAVIS Daily Report generated successfully.",
                to=ALERT_EMAIL_TO,
            )
            return 0
        else:
            print("[trigger_daily] FAILED ❌ (non-200 status)")
            send_email(
                subject="JRAVIS Daily Report ❌ FAILED",
                body=f"Backend returned HTTP {r.status_code}:\n{r.text[:500]}",
                to=ALERT_EMAIL_TO,
            )
            return 2

    except Exception as e:
        err_msg = f"[trigger_daily] ERROR: {e}"
        print(err_msg)
        send_email(
            subject="JRAVIS Daily Report ❌ ERROR",
            body=err_msg,
            to=ALERT_EMAIL_TO,
        )
        return 3


# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("[trigger_daily] Starting JRAVIS Daily Report Trigger...")
    exit_code = trigger_backend()
    print(f"[trigger_daily] Exiting with code {exit_code}")
