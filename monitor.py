import requests
import hashlib
import smtplib
from email.mime.text import MIMEText
import os
import json

# 👉 在这里加你要监控的两个网站
URLS = [
    "https://www.psoas.fi/en/locations/puistokatu-6/",
    "https://www.psoas.fi/en/vacant-apartments/"
]

def get_hash(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return hashlib.md5(response.text.encode()).hexdigest()

def send_email(changed_urls):
    msg = MIMEText("这些网页发生变化：\n\n" + "\n".join(changed_urls))
    msg['Subject'] = '网页变化提醒'
    msg['From'] = os.environ['EMAIL_USER']
    msg['To'] = os.environ['EMAIL_USER']

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(os.environ['EMAIL_USER'], os.environ['EMAIL_PASS'])
        server.send_message(msg)

def main():
    changed = []

    # 读取旧数据
    try:
        with open("last_hash.txt", "r") as f:
            old_hashes = json.load(f)
    except:
        old_hashes = {}

    new_hashes = {}

    # 遍历所有网站
    for url in URLS:
        new_hash = get_hash(url)
        new_hashes[url] = new_hash

        # 如果旧数据存在且不同 → 说明变化
        if url in old_hashes and old_hashes[url] != new_hash:
            changed.append(url)

    # 如果有变化 → 发邮件
    if changed:
        send_email(changed)

    # 保存新数据
    with open("last_hash.txt", "w") as f:
        json.dump(new_hashes, f)

if __name__ == "__main__":
    main()
