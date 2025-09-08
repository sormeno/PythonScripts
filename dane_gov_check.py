from lib.mail import *
from lib.mail_config import MAIL_TO
from lib.mail_config import TODOIST_BEARER
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time

MAIL_SUBJECT = 'dane.gov.pl - check '

now = datetime.now()
TODAY = now.strftime("%Y-%m-%d")

resources = [
    {"id": 5371, "name": "ZUW Urbex - Złotoryja"},
    {"id": 5648, "name": "Ander - Osada Magdalenka"},
    {"id": 5811, "name": "Ander - Osada Dzbenin"}
]

def check_resource(resource):
    url = f'https://api.dane.gov.pl/1.4/datasets/{resource["id"]}/resources/?created[term]={TODAY}'
    html = f"<tr><td>{resource['name']}</td>"
    try:
        response = requests.get(url)
    except Exception as e:
        html = html + "<td>{type(e)}</td><td></td><td></td><td></td></tr>"

    data = response.json()
    resource_exist = "<td style='color: green; font-weight: bold;'>OK</td>" if data.get('data') and len(data['data']) > 0 else "<td style='color: red; font-weight: bold;'>X</td>"
    html = html + resource_exist + "<td></td><td></td><td></td></tr>"
    return html

def check_resources(resources):
    html = "<table><tr><th>Dataset</th><th>Plik Istnieje</th><th>Liczba rekordów</th><th>Średnia cena</th><th>Średnia cena mkw</th></tr>"
    for resource in resources:
        html = html + check_resource(resource)

    return html + "</table>"

#try:
html = check_resources(resources)
#except Exception as e: 
#    html = f"<h5>Wystąpił nieznany błąd</h5>{e}"

style = """
<style>
  table, th, td {
    border: 1px solid black;  /* border for every cell */
    border-collapse: collapse; /* merge double borders */
  }
  th, td {
    padding: 8px;
  }
</style>
"""

header = f'<h2>Raport zasobów w dane.gov.pl w dniu {TODAY}</h2>'

msg_html = f'<html>{style}<head>{header}</head><body>{html}</body></html>'
smtp_client = SMTP()
smtp_client.send_email(MAIL_TO, MAIL_SUBJECT + TODAY, msg_html_content=msg_html)
smtp_client.close()
