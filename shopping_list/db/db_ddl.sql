PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE dishes (dish_id INTEGER PRIMARY KEY, dish_name TEXT, recipe_address TEXT, prep_time REAL, dish_type TEXT);
CREATE TABLE ingredients (ingredient_id INTEGER PRIMARY KEY, ingredient_name TEXT, unit TEXT);
CREATE TABLE shopping ( shopping_list_id INTEGER PRIMARY KEY,   shopping_date TEXT);
CREATE TABLE menus (shopping_list_id INTEGER, dish_id INTEGER, FOREIGN KEY(shopping_list_id) REFERENCES shopping(shopping_list_id), FOREIGN KEY(dish_id) REFERENCES dishes(dish_id));
CREATE TABLE dish_ingredients (dish_id INTEGER, ingredient_id INTEGER, quantity REAL, FOREIGN KEY(dish_id) REFERENCES dishes(id), FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id));
DELETE FROM sqlite_sequence;
COMMIT;