from lib.mail import *
from lib.mail_config import MAIL_TO
import os

with open('/home/filip/PythonScripts/eco-tram/stats.html', 'r') as file:
    content = file.read()

smtp_client = SMTP()
smtp_client.send_email(MAIL_TO, 'Tram API Statistics', msg_html_content=content)
smtp_client.close()

os.remove('/home/filip/PythonScripts/eco-tram/stats.html')