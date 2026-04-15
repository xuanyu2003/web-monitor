import requests
import hashlib
import smtplib
from email.mime.text import MIMEText
import os

URL = "https://example.com"

def get_page_hash():
    response = requests.get(URL)
    content = response.text
    return hashlib.md5(content.encode()).hexdigest()

def send_email():
    msg = MIMEText("网页发生变化！")
    msg['Subject'] = '网页变化提醒'
    msg['From'] = os.environ['EMAIL_USER']
    msg['To'] = os.environ['EMAIL_USER']

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(os.environ['EMAIL_USER'], os.environ['EMAIL_PASS'])
        server.send_message(msg)

def main():
    new_hash = get_page_hash()

    try:
        with open("last_hash.txt", "r") as f:
            old_hash = f.read()
    except:
        old_hash = ""

    if old_hash and new_hash != old_hash:
        send_email()

    with open("last_hash.txt", "w") as f:
        f.write(new_hash)

if __name__ == "__main__":
    main()
