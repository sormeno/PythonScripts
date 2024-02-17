from lib.mail import *
from lib.mail_config import MAIL_TO
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time

MAIL_SUBJECT = 'Dzień dobry!'

now = datetime.now()
today_meteo = now.strftime("%Y%m%d")
today_todoist = now.strftime("%Y-%m-%d")
today_kio = now.strftime("%Y").replace("20","")
today_kio = '23' #####to remove
kio_file_path = "/home/filip/PythonScripts/resources/kio.txt"

def get_meteo():
    return f'<h3>Pogoda na dziś</h3><img src="https://www.meteo.pl/um/metco/mgram_pict.php?ntype=0u&fdate={today_meteo}00&row=403&col=250&lang=pl">'

def get_today_inbox(url, headers, inbox_id):
    data = requests.get(url+'tasks',headers=headers)
    tasks = data.json()

    today_inbox=[]
    for task in tasks:
        if task["due"]!=None and task["due"]["date"]==today_todoist and task["project_id"]==inbox_id:
            today_inbox.append(task["due"]["string"]+"   "+task["content"])
    
    today_inbox.sort()
    result = '<h3>Dzisiejsze taski</h3>'
    for task in today_inbox:
        result = result + task + '<br>'
    return result

def get_kio():
    file = open(kio_file_path,"r")
    init_next = int(file.readline())
    next = init_next
    file.close()
    get_next = True
    result = ""
    
    while get_next:
        print(next)
        url = f"http://www.uzp.gov.pl/kio/informacje-o-toku-postepowania-odwolawczego?kio={next}%2F{today_kio}"
        page = requests.get(url, verify=False)
        soup = BeautifulSoup(page.content, 'html.parser')
        content = soup.find("div", {"class":"case-search__search-results"})
        paragraphs = ""
        for x in content:
            paragraphs= paragraphs+str(x)+"<br>"
        if "Generalna Dyrekcja Dróg Krajowych i Autostrad" in paragraphs:
            result = result + paragraphs
        if "Nie znaleziono odwołania o numerze" in paragraphs and init_next == next:
            result = result + "WARN: Przerwa w numeracji"
        if "Nie znaleziono odwołania o numerze" in paragraphs:
            get_next = False
            file = open(kio_file_path,"w")
            file.write(str(next))
            file.close()   
        next = next+1
        time.sleep(10)
 
    return result


url = 'https://api.todoist.com/rest/v2/'
headers = {"Authorization": "Bearer 8828bec13c255fd1fb38e50b46b8e4b69fd03fc2"}

try:
    todoist=get_today_inbox(url,headers,'2155964695')
except Exception as e: 
    todoist = f"<h5>Todoist Error</h5>{e}"
try:
    meteo = get_meteo()
except Exception as e: 
    meteo = f"<h5>Meteo Error</h5>{e}"
# try:
#     kio = get_kio()
# except Exception as e: 
#     kio = f"<h5>KIO Error</h5>{e}"

header = '<h2>Jestem kompetentny i zdolny do osiągnięcia swoich celów.</h2>'

msg_html = f'<html><head>{header}</head>{todoist}<br>{meteo}<body></body></html>'
smtp_client = SMTP()
smtp_client.send_email(MAIL_TO, MAIL_SUBJECT, msg_html_content=msg_html)
smtp_client.close()
