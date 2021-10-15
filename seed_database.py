import os, json, crud, model, server
import random as r

# Drop the database with dropdb
# Create the database with createdb
os.system('dropdb fgproject')
os.system('createdb fgproject')

# Use db.create_all to create tables

model.connect_to_db(server.app)
model.db.create_all()

crud.create_user('test@test.test', 'Test', '7357')

crud.create_char(1)

crud.create_cont('static/img/testbox.jpg')

crud.create_map(1, 'test')

x_cord = 0

while x_cord < 30:
    y_cord = 0
    while y_cord < 20:
        crud.create_tile(x_cord, y_cord, 1)
        y_cord +=1
    x_cord +=1
    