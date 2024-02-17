import subprocess

from lib.DB import DB
from shopping_list.config import DB_FILE

generate_menu_script = '/home/filip/PythonScripts/shopping_list/generate_menu.py'
prepare_shopping_list = '/home/filip/PythonScripts/shopping_list/prepare_shopping_list.py'
weeks = '6'

db = DB(DB_FILE)
if(db.execute_query("SELECT count(*) FROM shopping WHERE shopping_date is null")[0][0]==0):
    subprocess.Popen(['python', generate_menu_script, weeks])

subprocess.Popen(['python', prepare_shopping_list])