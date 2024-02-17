import random
import sys

from lib.DB import DB
import config

def create_shopping_list(num_lists):
    result = db.execute_query("SELECT MAX(shopping_list_id) FROM shopping")
    max_id = result[0][0] or 0
    lists = []

    for i in range(1, num_lists + 1):
        lists.append(max_id + i)
        db.execute_query("INSERT INTO shopping (shopping_list_id) VALUES (?)", (max_id + i,))
    return lists

def pick_random_dishes(dishes_num, dish_type):
    dishes = db.execute_query("SELECT dish_id FROM dishes WHERE dish_type = ? ORDER BY RANDOM() LIMIT ?", (dish_type, dishes_num))
    random.shuffle(dishes)
    return [dish[0] for dish in dishes]

def pick_meals(shoping_lists, type, dishes_num):
    meals = pick_random_dishes( 100, type)
    for list in shoping_lists:
        random_meals = random.sample(meals, dishes_num)
        for meal in random_meals:
            db.execute_query("INSERT INTO menus (shopping_list_id, dish_id) VALUES (?, ?)", (list, meal))

def main (weeks):
    shoping_lists = create_shopping_list(weeks)
    pick_meals(shoping_lists, 'dinner', 2)
    pick_meals(shoping_lists, 'breakfast', 6)


db = DB(config.DB_FILE)
main(int(sys.argv[1]))
