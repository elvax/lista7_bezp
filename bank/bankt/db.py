import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import check_password_hash, generate_password_hash


def get_db():
	if 'db' not in g:
		g.db = sqlite3.connect(
			current_app.config['DATABASE'],
			detect_types=sqlite3.PARSE_DECLTYPES
		)
		g.db.row_factory = sqlite3.Row

	return g.db

def close_db(e=None):
	db = g.pop('db', None)

	if db is not None:
		db.close()

def init_db():
	db = get_db()

	with current_app.open_resource('schema.sql') as f:
		db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
	"""Create new tables"""
	init_db()
	click.echo('Initialized the database.')

@click.command('show-users')
@with_appcontext
def show_users():
	db = get_db()
	users = db.execute('SELECT * FROM user')
	for user in users:
		click.echo(user['id'], nl=False)
		click.echo(user['username'])

@click.command('init-users')
@with_appcontext
def init_users():
	db = get_db()
	db.execute('''INSERT INTO admins ("admin_name", "password") 
		VALUES ("admin", "{}")'''
		.format(generate_password_hash('admin')))
	db.execute('''INSERT INTO user ("username", "email", "password") 
		VALUES ("alicja123", "alicja123@mail.com", "{}")'''
		.format(generate_password_hash('alicja123')))
	db.execute('''INSERT INTO user ("username", "email", "password") 
		VALUES ("sebastian123", "sebastian123@mail.com", "{}")'''
		.format(generate_password_hash('sebastian123')))
	db.commit()


def init_app(app):
	app.teardown_appcontext(close_db)
	app.cli.add_command(init_db_command)
	app.cli.add_command(show_users)
	app.cli.add_command(init_users)