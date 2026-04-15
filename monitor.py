import requests
import hashlib
import smtplib
from email.mime.text import MIMEText
import os
import json

# 监控目标
URLS = [
    "https://www.psoas.fi/en/locations/puistokatu-6/",
    "https://www.psoas.fi/en/vacant-apartments/"
]

def get_hash(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return hashlib.md5(response.text.encode()).hexdigest()
    except Exception as e:
        print(f"无法获取 {url}: {e}")
        return None

def send_email(changed_urls):
    user = os.environ.get('EMAIL_USER')
    password = os.environ.get('EMAIL_PASS')

    if not user or not password:
        print("错误: 环境变量未设置")
        return

    # 构建邮件正文，列出具体变化的网页
    url_list_str = "\n".join([f"- {url}" for url in changed_urls])
    body = f"你好！检测到以下网页内容发生变化：\n\n{url_list_str}\n\n请尽快检查！"
    
    msg = MIMEText(body)
    msg['Subject'] = '【提醒】PSOAS 网页发生更新！'
    msg['From'] = user
    msg['To'] = user

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(user, password)
            server.send_message(msg)
            print(f"邮件已发送，包含 {len(changed_urls)} 个变化。")
    except Exception as e:
        print(f"邮件发送失败: {e}")

def main():
    changed = []
    hash_file = "last_hash.txt"

    # 读取旧哈希值
    try:
        with open(hash_file, "r") as f:
            old_hashes = json.load(f)
    except:
        old_hashes = {}

    new_hashes = {}

    for url in URLS:
        current_hash = get_hash(url)
        if current_hash:
            new_hashes[url] = current_hash
            # 如果之前有记录且哈希不一致，记录该 URL
            if url in old_hashes and old_hashes[url] != current_hash:
                changed.append(url)
        elif url in old_hashes:
            # 如果请求失败，暂时保留旧哈希
            new_hashes[url] = old_hashes[url]

    if changed:
        send_email(changed)
    else:
        print("一切正常，网页无变化。")

    # 保存新的哈希值
    with open(hash_file, "w") as f:
        json.dump(new_hashes, f)

if __name__ == "__main__":
    main()
