
from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from bankt.db import get_db
from bankt.auth import login_required

import click


bp = Blueprint('logged', __name__, url_prefix='/logged')

@bp.route('/start', methods=('GET',))
@login_required
def start():
	id = session.get('user_id')
	user = get_db().execute(
		'SELECT username FROM user WHERE id = ?', (id,)
	).fetchone()
	return render_template('logged/start.html', user=user)
#	return '<h3> Wtiaj {} w swoim banku'.format(user['username'])


@bp.route('/transfer', methods=('GET', 'POST'))
@login_required
def transfer():
	if request.method == 'POST':
		error = None

		sender_id = session.get('user_id')

		account_no = request.form['account_no']
		amount = request.form['amount']
		title = request.form['title']
		
		if error is None:
			db = get_db()
			db.execute(
				'INSERT INTO transfers (sender_id, account_no, amount, title) VALUES (?, ?, ?, ?)',
				(sender_id, account_no, amount, title) 
			)
			db.commit()
			return redirect(url_for('logged.start'))

		flash(error)

	return render_template('logged/transfer.html')



@bp.route('/accepted', methods=('GET',))
@login_required
def accepted():
	error = None
	user_id = session.get('user_id')
	db = get_db()
	transfer_data = db.execute('SELECT * FROM transfers WHERE sender_id == ? ORDER BY id DESC LIMIT 1', (user_id,) ).fetchone()

	return render_template('logged/accepted.html', data=transfer_data)


@bp.route('/history', methods=('GET',))
@login_required
def history():
	user_id = session.get('user_id')
	db = get_db()
	transfers = db.execute(
		'SELECT title, account_no, amount FROM transfers WHERE sender_id == ? AND accepted == ? ORDER BY id DESC',
		(user_id, 1)
	).fetchall()
	return render_template('logged/history.html', transfers=transfers)

@bp.route('/pending', methods=('GET',))
@login_required
def pending():
	user_id = session.get('user_id')
	db = get_db()
	transfers = db.execute(
		'SELECT title, account_no, amount FROM transfers WHERE sender_id == ? AND accepted == ? ORDER BY id DESC',
		(user_id, 0)
	).fetchall()
	return render_template('logged/pending.html', transfers=transfers)


@bp.route('/search/', methods=('GET', 'POST',))
@login_required
def search():
	if request.method == 'POST':
		title = request.form['title']
		user_id = session.get('user_id')

		query = 'SELECT title, account_no, amount FROM transfers WHERE title == "{}" AND sender_id == "{}"'.format(title, user_id)
		db = get_db()
		results = db.execute(query).fetchall()

		return render_template('logged/search.html', results=results, query=query)

	return render_template('logged/search.html')
	# return 'title: {}'.format(title)


@bp.route('/comment/', methods=('GET', 'POST',))
@login_required
def comment():
	db = get_db()
	if request.method == 'POST':
		comment = request.form['comment']

		db.execute('INSERT INTO comments ("comment") VALUES ("{}")'.format(comment))
		db.commit()

	comments = db.execute('SELECT comment FROM comments').fetchall()

	return render_template('logged/comments.html', comments=comments)