import functools

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from bankt.db import get_db

import click


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		username = request.form['username']
		email =  request.form['email']
		password = request.form['password']

		db = get_db()
		error = None

		if not username:
			error = 'no username'
		elif not email:
			error = 'no email'
		elif not password:
			error = 'no password'
		elif db.execute(
			'SELECT id FROM user WHERE username = ?', (username,)
		).fetchone() is not None:
			error = 'user already registered'
		elif db.execute(
			'SELECT email FROM user WHERE email = ?', (email,)
		).fetchone() is not None:
			error = 'email already used'

		if error is None:
			db.execute(
				'INSERT INTO user (username, email, password) VALUES (?, ?, ?)',
				(username, email, generate_password_hash(password))
			)
			db.commit()
			return redirect(url_for('auth.login'))

		flash(error)

	return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		db = get_db()
		error = None
	
		# user = db.execute(
		# 	'SELECT * FROM user WHERE username = ?', (username,)
		# ).fetchone()
		
		query = 'SELECT * FROM user WHERE username ="' + username + '"'
		click.echo(query)
		user = db.execute(query).fetchone()
		click.echo(user['username'])


		if user is None:
			error = 'incorrect username'
		elif not check_password_hash(user['password'], password):
			error = 'incorrect password'

		if error is None:
			session.clear()
			session['user_id'] = user['id']
			return redirect(url_for('logged.start'))

		flash(error)

	return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
	user_id = session.get('user_id')
	admin_id = session.get('admin_id')

	if user_id is not None:
		g.user = get_db().execute(
			'SELECT * FROM user WHERE id = ?', (user_id,)
		).fetchone()
		g.admin = None
	elif admin_id is not None:
		g.admin = get_db().execute(
			'SELECT * FROM admins WHERE id = ?', (admin_id,)
		).fetchone()
		g.user = None
	else:
		g.user = None
		g.admin = None

@bp.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('index'))

def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for('auth.login'))

		return view(**kwargs)

	return wrapped_view

def admin_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.admin is None:
			return redirect(url_for('auth.login'))

		return view(**kwargs)

	return wrapped_view