import requests
import hashlib
import smtplib
from email.mime.text import MIMEText
import os
import json

# 要监控的网站
URLS = [
    "https://www.psoas.fi/en/locations/puistokatu-6/",
    "https://www.psoas.fi/en/vacant-apartments/"
]

def get_hash(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return hashlib.md5(response.text.encode()).hexdigest()
    except Exception as e:
        print(f"获取网页 {url} 失败: {e}")
        return None

def send_email(changed_urls):
    # 使用 .get() 避免 KeyError
    user = os.environ.get('EMAIL_USER')
    password = os.environ.get('EMAIL_PASS')

    if not user or not password:
        print("❌ 错误: 环境变量 EMAIL_USER 或 EMAIL_PASS 未设置！")
        return

    msg = MIMEText("这些网页发生变化：\n\n" + "\n".join(changed_urls))
    msg['Subject'] = 'PSOAS 房源变化提醒'
    msg['From'] = user
    msg['To'] = user

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(user, password)
            server.send_message(msg)
            print("✅ 邮件发送成功！")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

def main():
    changed = []
    hash_file = "last_hash.txt"

    # 读取旧数据
    try:
        with open(hash_file, "r") as f:
            old_hashes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        old_hashes = {}

    new_hashes = {}

    for url in URLS:
        new_hash = get_hash(url)
        if new_hash:
            new_hashes[url] = new_hash
            # 如果旧数据中已有该 URL 且哈希值不同
            if url in old_hashes and old_hashes[url] != new_hash:
                changed.append(url)
        else:
            # 如果这次获取失败，保留上次的哈希值
            if url in old_hashes:
                new_hashes[url] = old_hashes[url]

    if changed:
        print(f"检测到变化: {changed}")
        send_email(changed)
    else:
        print("暂无变化。")

    # 保存新数据
    with open(hash_file, "w") as f:
        json.dump(new_hashes, f)

if __name__ == "__main__":
    main()
