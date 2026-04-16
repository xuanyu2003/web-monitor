import requests
import smtplib
from email.mime.text import MIMEText
import os
from bs4 import BeautifulSoup

TARGET_URL = "https://www.psoas.fi/en/locations/puistokatu-6/"

def check_vacant(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Get full page text
        text = soup.get_text(separator=" ", strip=True)

        # Check keyword
        if "Vacant" in text:
            print("🚨 Vacant found on page!")
            return True

        print("✅ No vacant units found.")
        return False

    except Exception as e:
        print(f"❌ Error while checking page: {e}")
        return False


def send_email(url):
    user = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")

    if not user or not password:
        print("⚠️ Missing email credentials")
        return

    body = f"""🚨 ALERT: Vacant studio detected!

Check the page immediately:
{url}
"""

    msg = MIMEText(body)
    msg["Subject"] = "🏠 Housing Alert: Vacant Found"
    msg["From"] = user
    msg["To"] = user

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(user, password)
            server.send_message(msg)
            print("📧 Email sent successfully!")

    except Exception as e:
        print(f"❌ Email sending failed: {e}")


def main():
    if check_vacant(TARGET_URL):
        send_email(TARGET_URL)


if __name__ == "__main__":
    main()
