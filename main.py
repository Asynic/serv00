import os
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime, timezone, timedelta

import paramiko
import requests

server = os.getenv('SERVER', '[]')
mail = os.getenv('MAIL', None)
mail_psw = os.getenv('MAIL_PSW')


def ssh_multiple_connections(hosts_info, command):
    users = []
    hostnames = []
    for host_info in hosts_info:
        hostname = host_info['hostname']
        username = host_info['username']
        password = host_info['password']
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=hostname, port=22, username=username, password=password)
            stdin, stdout, stderr = ssh.exec_command(command)
            user = stdout.read().decode().strip()
            users.append(user)
            hostnames.append(hostname)
            ssh.close()
        except Exception as e:
            print(f"用户：{username}，连接 {hostname} 时出错: {str(e)}")
    return users, hostnames


user_list, hostname_list = ssh_multiple_connections(json.loads(server), 'whoami')

content = f"""
     Serv00-Login: 
Server: {hostname_list[0]}
Users:  {' / '.join(user_list)}
Time:   {datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}
IP:     {requests.get('https://api.ipify.org?format=json').json()['ip']}
"""


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
