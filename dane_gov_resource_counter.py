import xml.etree.ElementTree as ET
import urllib.request

from lib.mail import *
from lib.mail_config import MAIL_TO

URLS = [
    "https://vastbouw.pl/rcm/vastbouw_polska_2.xml",
    "https://vastbouw.pl/rcm/vastbouw_poznan_2.xml",
    "https://hyrna.pl/rcm/hyrna.xml",
    "https://dane.innotechs.pl/rcm/OPEN_DEVELOPMENT.xml",
    "https://dane.innotechs.pl/rcm/jb-atlantic-zorska.xml",
    "https://dane.innotechs.pl/rcm/gal-development-stary-mlyn.xml",
    "https://dane.innotechs.pl/rcm/gal-development-grabskiego.xml",
    "https://dane.innotechs.pl/rcm/ATRIUM_PBH.xml",
    "https://dane.innotechs.pl/rcm/ANDER.xml",
    "https://dane.innotechs.pl/rcm/AD_PROGRESS.xml"    
]

MAIL_SUBJECT = "Lista zbiorów zbliżająca się do 1000 zasobów"

style = "<style>body{font-family:Arial,sans-serif;font-size:13px;}</style>"

html_text = ""

for url in URLS:
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            root = ET.fromstring(response.read())

        resource_count = 0
        dataset_count = 0
        for element in root.iter():
            tag = element.tag.split("}")[-1]  # pomija namespace
            if tag == "resource":
                resource_count += 1
            elif tag == "dataset":
                dataset_count += 1

        if dataset_count == 0:
            continue
        wynik = (1000 - resource_count) / dataset_count
        if wynik < 20:
            html_text += (
                f"<p>W zbiorze {url} znajduje się {resource_count} zasobów. "
                f"Za {round(wynik, 1)} dni liczba przekroczy 1000.</p>"
            )

    except Exception as error:
        html_text += f"<p>Nie udało się pobrać/przetworzyć zbioru {url}: {error}</p>"

if html_text:
    header = f'<h2>Lista zbiorów zbliżająca się do 1000 zasobów</h2>'

    msg_html = f'<html>{style}<head>{header}</head><body>{html_text}</body></html>'
    smtp_client = SMTP()
    smtp_client.send_email(MAIL_TO, MAIL_SUBJECT, msg_html_content=msg_html)
    smtp_client.close()