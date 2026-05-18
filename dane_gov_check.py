from lib.mail import *
from lib.mail_config import MAIL_TO
from lib.mail_config import TODOIST_BEARER
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from io import BytesIO

MAIL_SUBJECT = 'dane.gov.pl - check '

REFDATE = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

resources = [
    {"id": 5648, "name": "Ander - Osada Magdalenka"},
    {"id": 5811, "name": "Ander - Osada Dzbenin"},
    {"id": 10249,"name": "JB Atlantic - Żorska"},
    {"id": 11147, "name": "Gal Development - Grabskiego"},
    {"id": 11146, "name": "Gal Development - Stary Młyn"},
    {"id": 14103, "name": "Open Development"},
    #{"id": 18562, "name": "ZUW Urbex - Złotoryja"},
    #{"id": 18557, "name": "ZUW Urbex - Infinity B1"},
    #{"id": 18559, "name": "ZUW Urbex - Infinity B2"},
    #{"id": 18560, "name": "ZUW Urbex - Murano"},
    {"id": 33036, "name": "Vastbouw - Positivo"},
    {"id": 33035, "name": "Vastbouw - OkiDoki"},
    {"id": 33033, "name": "Vastbouw - Aura Warszewo E1"},
    {"id": 33034, "name": "Vastbouw - Aura Warszewo E2"},
    #{"id": 15694, "name": "Vastbouw - Literatura E1"},
    {"id": 33037, "name": "Vastbouw - Literatura E2"},
    {"id": 18511, "name": "HYRNA - Hyrna"},
    {"id": 18510, "name": "M2R - Levityn"},
    {"id": 18507, "name": "AMS - Natura Park"},  
    {"id": 18509, "name": "AMS - Ruczaj Park"},     
    {"id": 31421, "name": "Gala Deweloper - Urzecze"},     
]

def get_stats(resource_content):    

    try:
        file_type = resource_content.get('attributes').get('format')
        url = resource_content.get('attributes').get('file_url')
    except:
        return 'E:', 'RESOURCE', 'ERROR', ''
    try:
        response = requests.get(url)
    except requests.exceptions.SSLError:
        # Retry with HTTP instead of HTTPS
        url_http = url.replace("https://", "http://", 1)
        response = requests.get(url_http)
    except Exception:
        return 'E:', 'FILE_URL', 'ERROR', ''

    # import file into df
    try:
        if file_type.lower() == 'csv':
            data_df = pd.read_csv(BytesIO(response.content))
        elif file_type.lower() in ['excel', 'xlsx', 'xls']:
            data_df = pd.read_excel(BytesIO(response.content))
        else:
            return 'E:','FILE','TYPE', ''
    except:
        return 'E:', 'DF', 'IMPORT', ''

    # Get total row count
    try:
        row_count = str(len(data_df))
    except:
        return 'E:', 'ROW', 'COUNT', ''


    # Filter for 'lokal mieszkalny' only
    try:
        property_type_col = next((col for col in data_df.columns
                            if "Rodzaj nieruchomości: lokal mieszkalny, dom jednorodzinny" in col.strip()), None)
        lokal_mieszkalny_df = data_df[data_df[property_type_col].str.lower() == 'lokal mieszkalny'].copy()
    except: 
        return 'E:', 'FILTER', 'ERROR', ''
        

    # Get apartament count
    try:
        apartament_count = str(len(lokal_mieszkalny_df))
    except:
        apartament_count = 'E'
    
    # Calculate average price per sqm for apartments
    try:
        price_sqm_col = "Cena m 2 powierzchni użytkowej lokalu mieszkalnego / domu jednorodzinnego [zł]"
        # Convert to numeric, coercing errors to NaN
        lokal_mieszkalny_df[price_sqm_col] = pd.to_numeric(
            lokal_mieszkalny_df[price_sqm_col].astype(str).str.replace(' ', '').str.replace(',', '.'), 
            errors='coerce'
        )
        avg_price_sqm = str(round(lokal_mieszkalny_df[price_sqm_col].mean()))
    except Exception as e:
        print(f"Error: {e}")
        avg_price_sqm = 'E'

    # Calculate average total price for apartments
    try:
        price_col = "Cena lokalu mieszkalnego lub domu jednorodzinnego będących przedmiotem umowy stanowiąca iloczyn ceny m2 oraz powierzchni [zł]"
        # Convert to numeric, coercing errors to NaN
        lokal_mieszkalny_df[price_col] = pd.to_numeric(
            lokal_mieszkalny_df[price_col].astype(str).str.replace(' ', '').str.replace(',', '.'), 
            errors='coerce'
        )
        avg_price = str(round(lokal_mieszkalny_df[price_col].mean()))
    except Exception as e:
        print(f"Error: {e}")
        avg_price = 'E'

    return row_count, avg_price, avg_price_sqm, apartament_count

def check_resource(resource):
    url = f'https://api.dane.gov.pl/1.4/datasets/{resource["id"]}/resources/?created[term]={REFDATE}'
    html = f"<tr><td>{resource['name']}</td>"
    #print(f"Processing {resource['name']}")
    try:
        response = requests.get(url)
    except Exception as e:
        html = html + f"<td>{type(e)}</td><td></td><td></td><td></td><td></td></tr>"

    try:
        data = response.json()
        data_exists = data.get('data') and len(data['data']) > 0
    except:
        data_exists = False

    if data_exists:
        resource_exist = td('OK')
        cnt, avg_price, avg_price_sqm, apartament_cnt = get_stats(data.get('data')[0])
        html = html + resource_exist + td(cnt) + td(apartament_cnt) + td(avg_price) + td(avg_price_sqm) + "</tr>"
    
    else: 
        resource_exist = f"{td('X')}X</td>"
        html = html + resource_exist + "<td></td><td></td><td></td><td></td></tr>"
      
    return html

def check_resources(resources):
    html = "<table><tr><th>Dataset</th><th>Plik Istnieje</th><th>Liczba rekordów</th><th>Liczba mieszkań</th><th>Średnia cena</th><th>Średnia cena mkw</th></tr>"
    for resource in resources:
        html = html + check_resource(resource)

    return html + "</table>"

def td(value):
    #check if value is number
    if value.isdigit():
        formatted_value = f"{int(value):,}".replace(",", " ")
        return f"<td style='color: green; font-weight: bold;'>{formatted_value}</td>"
    elif value == 'OK':
        return f"<td style='color: green; font-weight: bold;'>{value}</td>"
    else: 
        return f"<td style='color: red; font-weight: bold;'>{value}</td>"

html = check_resources(resources)

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

header = f'<h2>Raport zasobów w dane.gov.pl w dniu {REFDATE}</h2>'

msg_html = f'<html>{style}<head>{header}</head><body>{html}</body></html>'
smtp_client = SMTP()
smtp_client.send_email(MAIL_TO, MAIL_SUBJECT + REFDATE, msg_html_content=msg_html)
smtp_client.close()
