import sys

from lib.DB import DB
from lib.mail import SMTP
import config

def next_shopping_id():
    result = db.execute_query("SELECT MIN(shopping_list_id) FROM shopping WHERE shopping_date IS NULL")
    shopping_list_id = result[0][0] or 1
    return shopping_list_id

def register_shopping_list_delivery(shopping_list_id):
    db.execute_query("UPDATE shopping SET shopping_date = date('now') WHERE shopping_list_id = ?", (shopping_list_id,))

def shopping_list(shopping_list_id):
    return db.execute_query("""
SELECT
    i.ingredient_name as nazwa,
    CASE 
      WHEN SUM(di.quantity) = 0
        THEN NULL
      ELSE ROUND(SUM(di.quantity),1) 
    END as ilosc ,
    i.unit as jm
FROM dish_ingredients di
INNER JOIN dishes d ON di.dish_id = d.dish_id
INNER JOIN menus m ON d.dish_id = m.dish_id
INNER JOIN ingredients i ON di.ingredient_id = i.ingredient_id
WHERE m.shopping_list_id = ?
GROUP BY i.ingredient_id
ORDER BY i.ingredient_name
""", (shopping_list_id,))


def generate_html_shopping_list(shopping_list_id):    
    rows = shopping_list(shopping_list_id)
    
    html = '<h3>Lista zakupów</h3>'
    html += '<table style="border-collapse: collapse;">'
    html += '<tr style="border-bottom: 1px solid #ddd;"><th style="padding: 8px; border-bottom: 2px solid #ddd;">Nazwa</th><th style="padding: 8px; border-bottom: 2px solid #ddd;">Ilość</th><th style="padding: 8px; border-bottom: 2px solid #ddd;">Jm</th></tr>'
    for row in rows:
        html += f'<tr style="border-bottom: 1px solid #ddd;"><td style="padding: 8px; border-bottom: 1px solid #ddd;">{row[0]}</td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{row[1] if row[1] is not None else ""}</td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{row[2]}</td></tr>'
    html += '</table>'

    return html

def menu(shopping_list_id):
    return db.execute_query("""
    SELECT
        d.dish_name as Potrawa,
        d.dish_type,
        d.recipe_address as Przepis
    FROM dishes d
    INNER JOIN menus m ON d.dish_id = m.dish_id
    WHERE m.shopping_list_id = ?
    """, (shopping_list_id,))

def generate_html_menu(shopping_list_id):
    menu_items = menu(shopping_list_id)
    html = "<h2>Menu na przyszły tydzień</h2>"
    
    # Append dinners
    html += "<h3>Obiad</h3>"
    dinner_days = ["Niedziela", "Środa"]
    dinner_items = [item for item in menu_items if item[1] == "dinner"]
    
    for day, item in zip(dinner_days, dinner_items):
        dish_name, _, recipe_address = item
        html += f"{day}: <b>{dish_name}</b> - {recipe_address}<br>"
    
    # Append breakfasts
    html += "<h3>Śniadanie</h3>"
    breakfast_days = ["Niedziela", "Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek"]
    breakfast_items = [item for item in menu_items if item[1] == "breakfast"]
    
    for day, item in zip(breakfast_days, breakfast_items):
        dish_name, _, recipe_address = item
        html += f"{day}: <b>{dish_name}</b> - {recipe_address}<br>"
    
    return html

def send_email(message):    
    smtp_client = SMTP()
    smtp_client.send_email(config.MAIL_TO, config.MAIL_SUBJECT, msg_html_content=message)
    smtp_client.close()

def main():
    shopping_list_id = next_shopping_id()
    menu = generate_html_menu(shopping_list_id)
    shopping_list = generate_html_shopping_list(shopping_list_id)
    send_email('<html>' + menu +'<br>' + shopping_list + '</html>')
    register_shopping_list_delivery(shopping_list_id)

db = DB(config.DB_FILE)
main()
