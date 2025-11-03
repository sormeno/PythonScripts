from lib.mail import *
from lib.mail_config import MAIL_TO
from lib.mail_config import TODOIST_BEARER
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from io import BytesIO

MAIL_SUBJECT = 'dane.gov.pl - check '

now = datetime.now()
TODAY = now.strftime("%Y-%m-%d")

resources = [
    {"id": 5648, "name": "Ander - Osada Magdalenka"},
    {"id": 5811, "name": "Ander - Osada Dzbenin"},
    {"id": 10249,"name": "JB Atlantic - Żorska"},
    {"id": 11147,"name": "Gal Development - Grabskiego"},
    {"id": 11146,"name": "Gal Development - Stary Młyn"},
    {"id": 14103,"name": "Open Development"},
    {"id": 5371, "name": "ZUW Urbex - Złotoryja"},
    {"id": 11568,"name": "Vastbouw - Positivo"},
    {"id": 11567,"name": "Vastbouw - OkiDoki"},
    {"id": 11566,"name": "Vastbouw - Aura Warszewo E1"},
    {"id": 11267,"name": "Vastbouw - Aura Warszewo E2"},
    {"id": 8774, "name": "HYRNA - Hyrna"},
    {"id": 8776, "name": "M2R - Levityn"},
    {"id": 9025, "name": "AMS - Natura Park"},  
    {"id": 9023, "name": "AMS - Ruczaj Park"},
]

def get_stats(resource_content):    

    file_type = resource_content.get('attributes').get('format')
    url = resource_content.get('attributes').get('file_url')
    response = requests.get(url)

    if file_type.lower() == 'csv':
        data_df = pd.read_csv(BytesIO(response.content))
    elif file_type.lower() in ['excel', 'xlsx', 'xls']:
        data_df = pd.read_excel(BytesIO(response.content))
    else:
        return '','',''

    # Get total row count
    row_count = str(len(data_df))
    #print(data_df.columns.tolist())

    property_type_col = next((col for col in data_df.columns
                         if "Rodzaj nieruchomości: lokal mieszkalny, dom jednorodzinny" in col.strip()), None)

    # Filter for 'lokal mieszkalny' only
    lokal_mieszkalny_df = data_df[data_df[property_type_col] == 'lokal mieszkalny']

    # Calculate average price per sqm for apartments
    avg_price_sqm = str(round(lokal_mieszkalny_df["Cena m 2 powierzchni użytkowej lokalu mieszkalnego / domu jednorodzinnego [zł]"].astype(int).mean()))

    # Calculate average total price for apartments
    avg_price = str(round(lokal_mieszkalny_df["Cena lokalu mieszkalnego lub domu jednorodzinnego będących przedmiotem umowy stanowiąca iloczyn ceny m2 oraz powierzchni [zł]"].astype(int).mean()))

    return row_count, avg_price, avg_price_sqm

def check_resource(resource):
    url = f'https://api.dane.gov.pl/1.4/datasets/{resource["id"]}/resources/?created[term]={TODAY}'
    html = f"<tr><td>{resource['name']}</td>"
    #print(f"Processing {resource['name']}")
    try:
        response = requests.get(url)
    except Exception as e:
        html = html + "<td>{type(e)}</td><td></td><td></td><td></td></tr>"

    data = response.json()
    if data.get('data') and len(data['data']) > 0:
        resource_exist = "<td style='color: green; font-weight: bold;'>OK</td>"  
        # cnt, avg_price, avg_price_sqm = get_stats(data.get('data')[0]) #TODO fix get_stats
        # html = html + resource_exist + f"<td>{cnt}</td><td>{avg_price}</td><td>{avg_price_sqm}</td></tr>"
        html = html + resource_exist + "<td></td><td></td><td></td></tr>"
    
    else: 
        resource_exist = "<td style='color: red; font-weight: bold;'>X</td>"
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
