from metalreal import app
from flask import session, redirect, url_for, render_template, request, flash
from jinja2 import Markup
from sqlalchemy import create_engine, Table, Column, MetaData, ForeignKey
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.sql import select, insert
from sqlalchemy.dialects.postgresql import \
    ARRAY, BIGINT, BIT, BOOLEAN, BYTEA, CHAR, CIDR, DATE, \
    DOUBLE_PRECISION, ENUM, FLOAT, INET, INTEGER, INTERVAL, \
    MACADDR, NUMERIC, REAL, SMALLINT, TEXT, TIME, TIMESTAMP, \
    UUID, VARCHAR

unescape=Markup

"""
	Database preparation
"""
engine = create_engine("postgresql+psycopg2://tester:tester@localhost:5432/metalreal_dev", client_encoding='utf8', echo=True)
metadata = MetaData()
Chapters = Table('chapters', metadata,
		Column('chapter_id', VARCHAR(10), primary_key = True),
		Column('title', VARCHAR(120), nullable=False),
		Column('content', TEXT, nullable=False),
		Column('updated_at', TIMESTAMP, default='NOW', onupdate='NOW')
	)
metadata.create_all(engine)
metadata.bind = engine


def require_admin_auth(f):
	def decorated(*args, **kargs):
		if 'admin' in session:
			return f(*args, **kargs)
		else:
			return redirect(url_for('admin_login'))
	decorated.__name__ = f.__name__
	return decorated

@app.route('/admin/')
@app.route('/admin/chapters/')
@require_admin_auth
def admin_index():
	chapters = Chapters.select(order_by=Chapters.c.chapter_id).execute()
	return render_template('admin/index.html', chapters=chapters, area='chapter', unescape=unescape )

@app.route('/admin/chapters/new', methods=['GET', 'POST'])
@require_admin_auth
def admin_chapter_new():
	if request.method == 'GET':
		return render_template('admin/chapters/new.html', area='chapter/new', unescape=unescape )
	else:
		insert_query = Chapters.insert().values(chapter_id=request.form['chapter_id'], 
																						title=request.form['title'], 
																						content=request.form['content']
																						)

		try:
			if request.form['title'] == '' or request.form['content'] == '':
				raise
			insert_query.execute()
			flash('Chapter was created', 'success')
			return redirect(url_for('admin_index'))

		except Exception, e:
			# Add flash by checking all possible cause that raise the exception
			if request.form['title'] == '':
				flash("Title can't be blank", 'error')

			if request.form['content'] == '':
				flash("Content can't be blank", 'error')

			if 'chapters_pkey' in e.message:
				flash('Chapter number is duplicate', 'error')

			return render_template('admin/chapters/new.html', area='chapter/new', unescape=unescape, chapter=request.form )

@app.route('/admin/login/', methods=['GET', 'POST'])
def admin_login():
	if 'admin' in session and session['admin'] == 'admin':
		return redirect(url_for('admin_index'))

	if request.method == 'POST':
		if request.form['username'] == 'admin' and request.form['password'] == 'admin':
			session['admin'] = request.form['username']
			return redirect(url_for('admin_index'))
	return render_template('admin/login.html')

@app.route('/admin/logout/')
def admin_logout():
	session.pop('admin', None)
	return redirect(url_for('admin_login'))