import os
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime, timezone, timedelta

import paramiko
import requests

server = json.loads(os.getenv('SERVER', '[]'))
mail = os.getenv('MAIL', None)
mail_psw = os.getenv('MAIL_PSW')

host = server['host']
psw = server['psw']
users = server['users']
failed = []


def connecting(command='whoami'):
    success = []
    for username in users:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, port=22, username=username, password=psw)
            stdin, stdout, stderr = ssh.exec_command(command)
            user = stdout.read().decode().strip()
            print(f'{user} success!')
            success.append(user)
            ssh.close()
        except Exception as e:
            print(f"{username} while connecting {host} cause error: {str(e)}")
            failed.append(username)
    return success


user_login = connecting()
content = f"""
     Serv00-Login: 
Server: {host} *
Users:  {' / '.join(user_login)}
Time:   {datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}
IP:     {requests.get('https://api.ipify.org?format=json').json()['ip']}
"""

if failed:
    s = f'\nFailed:  {" / ".join(failed)}\n'
    content = content.replace('*', s)


def mail_push(sender, receiver, info, ):
    smtp_server = 'smtp.qq.com'  # smtp服务器
    smtp_port = 465  # smtp端口

    # 配置服务器
    stmp = smtplib.SMTP_SSL(smtp_server, smtp_port)
    stmp.login(sender, mail_psw)

    message = MIMEText(info, 'plain', 'utf-8')  # 发送的内容
    message['From'] = sender
    message['To'] = receiver

    subject = 'Serv00-Login'
    message['Subject'] = Header(subject, 'utf-8')  # 邮件标题

    try:
        stmp.sendmail(sender, receiver, message.as_string())
        print(f'邮件发送成功: {info}')
    except smtplib.SMTPException as e:
        print(f'邮件发送失败 --- {e!r}')


mail_push(mail, mail, content)
