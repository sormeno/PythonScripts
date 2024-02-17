import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
from lib.mail_config import PORT,HOST,PASSWORD,MAIL_FROM


class SMTP:

    PORT=PORT
    HOST=HOST
    PASSWORD=PASSWORD
    MAIL_FROM=MAIL_FROM

    def __init__(self):
        self.s = smtplib.SMTP(host=SMTP.HOST, port=SMTP.PORT)
        self.msg_from = SMTP.MAIL_FROM
        self.s.starttls()
        self.s.ehlo()
        try:
            self.s.login(self.msg_from, SMTP.PASSWORD)
            self.s.ehlo()
        except:
            sys.exit()


    def close(self):
        try:
            self.s.ehlo()
            self.s.quit()
        except Exception as e:
            print(f'Mail login to {self.msg_from} has not been closed with exception {e}', exc_info=True)


    def send_email(self,msg_to, msg_subject, msg_content = None, msg_html_content = None):
        msg = MIMEMultipart()
        msg_content = msg_html_content if msg_html_content else msg_content
        msg_type = 'html' if msg_html_content else 'plain'

        msg['From'] = self.msg_from
        msg['To'] = msg_to
        msg['Subject'] = msg_subject
        msg.attach(MIMEText(msg_content, msg_type))
        self.s.ehlo()
        self.s.send_message(msg)
        del msg
