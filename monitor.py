import requests
import hashlib
import smtplib
from email.mime.text import MIMEText
import os
import json
from bs4 import BeautifulSoup

# 只监控这一个具体页面
TARGET_URL = "https://www.psoas.fi/en/locations/puistokatu-6/"

def get_studio_status(url):
    """专门解析网页中是否有空置的 Studio"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. 寻找房源信息区域 (PSOAS 典型的房源列表容器)
        apt_container = soup.find('div', class_='location-apartments')
        
        if not apt_container:
            # 如果没找到房源区域，可能是页面改版或抓取被挡
            print("未找到房源容器，请检查网页结构。")
            return "No container found"

        # 2. 提取文本并过滤噪音
        # 我们只关心是否出现 "Studio" 和 "Vacant" 这种关键字
        all_text = apt_container.get_text(separator=' ', strip=True)
        
        # 3. 这里的逻辑是：如果文本里包含 'Studio'，我们就记录下这段文本
        # 这样只有当 Studio 的状态或描述变动时，才会触发邮件
        if "Studio" in all_text:
            print("发现 Studio 相关信息！")
            return all_text
        else:
            print("目前没有 Studio 信息。")
            return "No Studio available"

    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        return None

def send_email(url):
    user = os.environ.get('EMAIL_USER')
    password = os.environ.get('EMAIL_PASS')
    
    if not user or not password:
        print("⚠️ 环境变量缺失，无法发送邮件")
        return

    body = f"🚨 警报！Puistokatu 6 房源状态发生变化！\n\n可能出现了空置的 Studio，请立即查看：\n{url}"
    
    msg = MIMEText(body)
    msg['Subject'] = '【房源提醒】Puistokatu 6 状态更新'
    msg['From'] = user
    msg['To'] = user

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(user, password)
            server.send_message(msg)
            print("🚀 邮件通知已发出")
    except Exception as e:
        print(f"❌ 邮件发送异常: {e}")

def main():
    hash_file = "last_hash.txt"
    current_status = get_studio_status(TARGET_URL)
    
    if current_status is None:
        return # 抓取失败时不操作

    # 计算当前状态的哈希值
    current_hash = hashlib.md5(current_status.encode('utf-8')).hexdigest()

    # 读取历史记录
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            old_hash = f.read().strip()
    else:
        old_hash = ""

    # 只有当哈希值变化，且当前不是“无房”状态时发送（或者你可以根据需求调整）
    if old_hash and current_hash != old_hash:
        print("📢 检测到房源状态变化！")
        send_email(TARGET_URL)
    else:
        print("✅ 状态未变，继续监控...")

    # 更新历史记录
    with open(hash_file, "w") as f:
        f.write(current_hash)

if __name__ == "__main__":
    main()
