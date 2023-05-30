import smtplib
from email.mime.text import MIMEText


def send_mail(mail, password):
    # QQ邮箱服务器地址
    mail_host = 'smtp.qq.com'
    # QQ用户名
    mail_user = 'xxxxx@qq.com'
    # 密码(部分邮箱为授权码)
    mail_pass = 'xxxxxx'

    # 邮件内容设置
    msg = MIMEText("""
       亲爱的用户,

       欢迎注册StarAI账号。您的账号密码是: """ + password + """

       请妥善保管此密码并不要与他人共享。

       欢迎加入StarAI大家庭!
       最佳问候,
       StarAI团队
       """, 'plain', 'utf-8')
    msg['From'] = mail_user
    msg['To'] = mail
    msg['Subject'] = '欢迎加入StarAI!'

    # 发送邮件
    try:
        server = smtplib.SMTP_SSL(mail_host)
        server.connect(mail_host, 465)
        server.login(mail_user, mail_pass)
        server.sendmail(mail_user, mail, msg.as_string())
        server.quit()
        return True
    except smtplib.SMTPException as e:
        print(e)
        return False