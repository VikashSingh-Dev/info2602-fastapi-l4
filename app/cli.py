import typer
import csv
from tabulate import tabulate
from sqlmodel import select
from app.database import create_db_and_tables, get_cli_session, drop_all
from app.models import *
from app.auth import encrypt_password

cli = typer.Typer()

@cli.command()
def initialize():
    with get_cli_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = RegularUser(username='bob', email='bob@mail.com',password=encrypt_password('bobpass'))
        rick = RegularUser(username='rick', email='rick@mail.com', password=encrypt_password('rickpass'))
        sally = RegularUser(username='sally', email='sally@mail.com', password=encrypt_password('sallypass'))
        db.add_all([bob, rick, sally])  #add all can save multiple objects at once
        db.commit()

        with open('todos.csv') as file:
            reader = csv.DictReader(file)
            for row in reader:
                new_todo = Todo(text=row['text'])  #create object
                #update fields based on records
                new_todo.done = True if row['done'] == 'true' else False
                new_todo.user_id = int(row['user_id'])
                db.add(new_todo)  #queue changes for saving
            db.commit()

        print("Database Initialized")

@cli.command()
def list_todos():
    with get_cli_session() as db: # Get a connection to the database
        data = []
        for todo in db.exec(select(Todo)).all():
            data.append(
                [todo.text, todo.done, todo.user.username,
                todo.get_cat_list()])
        print(tabulate(data, headers=["Text", "Done", "User", "Categories"]))

if __name__ == "__main__":
    cli()