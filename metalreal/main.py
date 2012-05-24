from metalreal import app
from flask import session, redirect, url_for, render_template, request, flash
from jinja2 import Markup
from sqlalchemy import create_engine, Table, Column, MetaData, ForeignKey, and_
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.sql import select, insert
from sqlalchemy.dialects.postgresql import \
    ARRAY, BIGINT, BIT, BOOLEAN, BYTEA, CHAR, CIDR, DATE, \
    DOUBLE_PRECISION, ENUM, FLOAT, INET, INTEGER, INTERVAL, \
    MACADDR, NUMERIC, REAL, SMALLINT, TEXT, TIME, TIMESTAMP, \
    UUID, VARCHAR
import markdown

unescape=Markup

"""
	Database preparation
"""
engine = create_engine("postgresql+psycopg2://tester:tester@localhost:5432/metalreal_dev", 
												client_encoding='utf8', echo=True)
metadata = MetaData()
Chapters = Table('chapters', metadata,
		Column('chapter_id', VARCHAR(10), primary_key = True),
		Column('title', VARCHAR(120), nullable=False),
		Column('content', TEXT, nullable=False),
		Column('updated_at', TIMESTAMP, default='NOW', onupdate='NOW')
	)
RequiredChapters = Table('required_chapters', metadata,
		Column('chapter_id', None, ForeignKey('chapters.chapter_id'), primary_key=True),
		Column('required_id', None, ForeignKey('chapters.chapter_id'), primary_key=True)
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
	chapters = [ row['chapter_id']+' '+row['title'] for row in select([Chapters.c.chapter_id,
																																		 Chapters.c.title]).execute()]

	if request.method == 'GET':
		return render_template('admin/chapters/new.html', area='chapter/new',
														 unescape=unescape, chapters=chapters )
	else:
		insert_query = Chapters.insert().values(chapter_id=request.form['chapter_id'], 
																						title=request.form['title'], 
																						content=request.form['content']
																						)
		try:
			if request.form['title'] == '' or request.form['content'] == '':
				raise
			insert_query.execute()
			if('required_chapters[]' in request.form):
				for required_chapter in request.form.getlist('required_chapters[]'):
					RequiredChapters.insert().values(chapter_id=request.form['chapter_id'],
																					required_id=required_chapter).execute()
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

			return render_template('admin/chapters/new.html', area='chapter/new', 
															unescape=unescape, chapter=request.form, chapters=chapters )

@app.route('/admin/chapters/edit/<string:chapter_id>', methods=['GET', 'POST'])
@require_admin_auth
def admin_chapter_edit(chapter_id):
	chapters = [ row['chapter_id']+' '+row['title'] for row in select([Chapters.c.chapter_id, Chapters.c.title],
																														 Chapters.c.chapter_id!=chapter_id).execute()]
	required_query = select([	RequiredChapters.c.required_id, Chapters.c.title],
													and_(RequiredChapters.c.chapter_id==chapter_id,
														RequiredChapters.c.required_id==Chapters.c.chapter_id)).execute()
	required_chapters = [row['required_id'] + ' ' + row['title'] for row in required_query]

	if request.method == 'GET':
		chapter =  Chapters.select().where(Chapters.c.chapter_id==chapter_id).execute().fetchone()

		return render_template('admin/chapters/edit.html', area='chapter/edit', unescape=unescape, 
														chapter=chapter, chapters=chapters, required_chapters=required_chapters )
	else:
		update_query = Chapters.update().values(chapter_id=request.form['chapter_id'],
																						title=request.form['title'],
																						content=request.form['content']
																						).where(Chapters.c.chapter_id==chapter_id)
		try:
			if request.form['title'] == '' or request.form['content'] == '':
				raise
			RequiredChapters.delete().where(RequiredChapters.c.chapter_id == chapter_id).execute()
			update_query.execute()
			if('required_chapters[]' in request.form):
				for required_chapter in request.form.getlist('required_chapters[]'):
					RequiredChapters.insert().values(chapter_id=request.form['chapter_id'],
																					required_id=required_chapter).execute()
			flash('Chapter has been updated', 'success')
			return redirect(url_for('admin_index'))
		except Exception, e:
			# Add flash by checking all possible cause that raise the exception
			print e
			if request.form['title'] == '':
				flash("Title can't be blank", 'error')

			if request.form['content'] == '':
				flash("Content can't be blank", 'error')

			if 'chapters_pkey' in e.message:
				flash('Chapter number is duplicate', 'error')

			return render_template('admin/chapters/edit.html', area='chapter/new', unescape=unescape, 
															chapter=request.form, chapters=chapters, required_chapters=required_chapters )

@app.route('/admin/chapters/delete/<string:chapter_id>')
@require_admin_auth
def admin_chapter_delete(chapter_id):
	try:
		Chapters.delete().where(Chapters.c.chapter_id == chapter_id).execute()
		flash('Chapter was deleted')
	except Exception:
		flash('Unable to delete chapter')
		return redirect(url_for('admin_index'))
	return redirect(url_for('admin_index'))

@app.route('/markdown_process', methods=['POST'])
def markdown_process():
	if request.is_xhr and 'markdown' in request.form:
		return markdown.markdown(request.form['markdown'])
	else:
		return ""

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