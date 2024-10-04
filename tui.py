import json
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pymongo import MongoClient

# 连接到MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['MBGNEWs']


def get_random_documents():
    # 定义集合
    zgc_collection = db['zgc']
    cctv_collection = db['cctv']

    # 随机提取5个文档
    zgc_docs = list(zgc_collection.aggregate([{"$sample": {"size": 5}}]))
    cctv_docs = list(cctv_collection.aggregate([{"$sample": {"size": 5}}]))

    # 构造json数据
    result = {
        "zgc": [{"title": doc.get('title', ''), "link": doc.get('link', '')} for doc in zgc_docs],
        "cctv": [{"title": doc.get('title', ''), "link": doc.get('link', '')} for doc in cctv_docs]
    }

    # 将结果转为json字符串
    json_result = json.dumps(result, ensure_ascii=False, indent=4)
    return json_result


def parse_and_send_email(news_json, recipient_email):
    # 解析 JSON 数据
    news_data = json.loads(news_json)

    # 生成邮件内容
    email_content = "<h3>中关村今日新闻：</h3>"
    for item in news_data['zgc']:
        email_content += f'<p><a href="{item["link"]}" target="_blank">{item["title"]}</a></p>'

    email_content += "<h3>CCTV今日新闻：</h3>"
    for item in news_data['cctv']:
        email_content += f'<p><a href="{item["link"]}" target="_blank">{item["title"]}</a></p>'

    # 创建邮件
    sender_email = "soryecker@163.com"  # 替换为发件人邮箱
    sender_password = "YZqXUrNyN23cEKrS"  # 替换为发件人邮箱密码
    subject = "今日新闻推送"

    # 设置邮件头信息
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # 将内容加入邮件正文
    msg.attach(MIMEText(email_content, 'html'))

    # 连接到邮件服务器并发送邮件
    try:
        with smtplib.SMTP('smtp.163.com', 25) as server:  # 替换为你的SMTP服务器地址
            server.starttls()  # 启用 TLS
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            # print("邮件发送成功!")
    except Exception as e:
        print(f"邮件发送失败: {e}")


def extract_emails_from_users():
    # 连接到 MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['MBGNEWs']
    user_collection = db['user']

    # 存储所有包含 email 的用户 email 地址
    email_list = []

    # 遍历 user 集合中的每一个文档
    for user in user_collection.find():
        if 'email' in user:  # 检查是否存在 email 字段
            email_list.append(user['email'])  # 提取 email 并存入列表

    return email_list

# 调用函数并打印结果
if __name__ == "__main__":
    json_data = get_random_documents()
    emails = extract_emails_from_users()
    # recipient_email = "soryecker@163.com"  # 替换为收件人邮箱
    for email in emails:
        print(f'[+]{email} 发送成功!')
        parse_and_send_email(json_data, email)
