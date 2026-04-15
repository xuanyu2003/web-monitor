import requests
import hashlib
import smtplib
from email.mime.text import MIMEText
import os
import json

# --- 配置区 ---
# 你要监控的网站列表
URLS = [
    "https://www.psoas.fi/en/locations/puistokatu-6/",
    "https://www.psoas.fi/en/vacant-apartments/"
]

def get_hash(url):
    """抓取网页并返回内容的 MD5 哈希值"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        # 过滤掉过短的内容（防止抓取到错误的空白页）
        if len(response.text) < 100:
            return None
        return hashlib.md5(response.text.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"❌ 抓取失败 {url}: {e}")
        return None

def send_email(changed_urls):
    """发送告知具体 URL 变化的邮件"""
    user = os.environ.get('EMAIL_USER')
    password = os.environ.get('EMAIL_PASS')

    if not user or not password:
        print("⚠️ 未配置环境变量 EMAIL_USER 或 EMAIL_PASS，取消发送")
        return

    # 格式化变化的 URL 列表
    url_list_str = "\n".join([f"🔗 {url}" for url in changed_urls])
    body = f"你好！检测到以下网页内容发生变化：\n\n{url_list_str}\n\n请尽快检查房源！"
    
    msg = MIMEText(body)
    msg['Subject'] = '【房源变动提醒】PSOAS 网页更新了！'
    msg['From'] = user
    msg['To'] = user

    try:
        # 使用 Gmail 的 SMTP 服务器（如果是其他邮箱请更换）
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(user, password)
            server.send_message(msg)
            print("🚀 邮件已成功发送！")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

def main():
    hash_file = "last_hash.txt"
    changed = []

    # 1. 加载上一次的历史记录
    if os.path.exists(hash_file):
        try:
            with open(hash_file, "r") as f:
                old_hashes = json.load(f)
        except:
            old_hashes = {}
    else:
        old_hashes = {}

    new_hashes = {}

    # 2. 检查每个 URL
    print("🔍 正在检查网页内容...")
    for url in URLS:
        current_hash = get_hash(url)
        if current_hash:
            new_hashes[url] = current_hash
            # 如果旧记录存在，且哈希值发生了变化
            if url in old_hashes and old_hashes[url] != current_hash:
                changed.append(url)
        elif url in old_hashes:
            # 如果本次请求失败，保留旧哈希，避免下次因恢复正常而误报
            new_hashes[url] = old_hashes[url]

    # 3. 只有当变化列表不为空时，才发邮件
    if changed:
        print(f"📢 检测到 {len(changed)} 个网页发生变化，准备发送邮件...")
        send_email(changed)
    else:
        print("✅ 网页内容未变，不发送邮件。")

    # 4. 保存当前的哈希值到文件（供下次对比）
    with open(hash_file, "w") as f:
        json.dump(new_hashes, f)

if __name__ == "__main__":
    main()
