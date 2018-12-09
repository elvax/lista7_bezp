from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from bankt.db import get_db
from bankt.auth import login_required, admin_required
from werkzeug.security import check_password_hash, generate_password_hash

import click

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
    
        user = db.execute(
          'SELECT * FROM admins WHERE admin_name = ?', (username,)
        ).fetchone()
        
        if user is None:
            error = 'incorrect username'
        elif not check_password_hash(user['password'], password):
            error = 'incorrect password'

        if error is None:
            session.clear()
            session['admin_id'] = user['id']
            g.user = user
            return redirect(url_for('admin.start'))

        flash(error)

    return render_template('admin/login.html')

@bp.route('/start', methods=('GET', 'POST'))
@admin_required
def start():
    db = get_db()
    if request.method == 'POST':
        id_to_accept = request.form['id']

        db.execute(
            '''UPDATE transfers
                    SET accepted = 1
                WHERE
                    id == ?''', (id_to_accept,)
            )
        db.commit()


    # dodać join i nazwa nadawcy
    data = db.execute(
        'SELECT id, account_no, amount, title FROM transfers WHERE accepted == 0'
        ).fetchall()

    return render_template('admin/start.html', data=data)