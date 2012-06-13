from metalreal import app
from metalreal.database import engine, Chapter, Question
from flask import session, redirect, url_for, render_template, request, flash, jsonify
from jinja2 import Markup
from sqlalchemy.orm import sessionmaker, exc
import markdown
import metalreal.database
import metalreal.error_pages

unescape = Markup
Session = sessionmaker(bind=engine)

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
  sess = Session()
  # Query all chapters
  chapters = sess.query(Chapter).order_by(Chapter.chapter_id).all()
  return render_template('admin/index.html', 
                        chapters=chapters,
                        area='chapter',
                        unescape=unescape)

@app.route('/admin/chapters/new', methods=['GET', 'POST'])
@require_admin_auth
def admin_chapter_new():
  sess = Session()
  # Query for all chapters so it will be used as chapters that
  # can be required
  chapters_query = sess.query(Chapter.chapter_id, Chapter.title).all()
  chapters = [c_id + ' ' + title for c_id, title in chapters_query]
  if request.method == 'GET':
    return render_template('admin/chapters/new.html', 
                          area='chapter/new',
                          unescape=unescape,
                          chapters=chapters)
  else:
    try:
      if request.form['title'] == '' or request.form['content'] == '':
        raise Exception()
      # Create new chapter
      new_chapter = Chapter(request.form['chapter_id'],
                            request.form['title'],
                            request.form['content'])
      if('required_chapters[]' in request.form):
        # Add required chapters
        for required_chapter in request.form.getlist('required_chapters[]'):
          required = sess.query(Chapter).filter_by(chapter_id=required_chapter).one()
          new_chapter.required_chapters.append(required)
      # Add new chapter to sqlalchemy.session
      sess.add(new_chapter)
      sess.commit()
      flash('Chapter was created', 'success')
      return redirect(url_for('admin_index'))
    except Exception, e:
      # Roll transaction in sqlalchemy.session back
      sess.rollback()
      # Add flash by checking all possible cause that raise the exception
      if request.form['title'] == '':
        flash("Title can't be blank", 'error')
      elif request.form['content'] == '':
        flash("Content can't be blank", 'error')
      elif 'chapters_pkey' in e.message:
        flash('Chapter number is duplicate', 'error')
      else:
        # Because now an exception isn't specific
        # so we raise it if we don't know what it is
        raise e

      return render_template('admin/chapters/new.html',
                            area='chapter/new', 
                            unescape=unescape,
                            chapter=request.form,
                            chapters=chapters)

@app.route('/admin/chapters/edit/<string:chapter_id>', 
          methods=['GET', 'POST'])
@require_admin_auth
def admin_chapter_edit(chapter_id):
  sess = Session()
  try:
    # Query for all chapters so it will be used as chapters that
    # can be required
    chapters_query = sess.query(Chapter.chapter_id,
                                Chapter.title).filter(Chapter.chapter_id != chapter_id).all()
    chapters = [ id + ' ' + title for id, title in chapters_query]
    chapter = sess.query(Chapter).filter_by(chapter_id=chapter_id).one()
    # Query required chapter of request chapter
    required_chapters = [req.chapter_id + ' ' + req.title for req in chapter.required_chapters]

    if request.method == 'GET':
      return render_template('admin/chapters/edit.html',
                            area='chapter/edit',
                            unescape=unescape,
                            chapter=chapter,
                            chapters=chapters,
                            required_chapters=required_chapters)
    else:
      try:
        # Update chapter data where chapter_id is matched
        chapter.chapter_id=request.form['chapter_id']
        chapter.title=request.form['title']
        chapter.content=request.form['content']

        # Raise an exception if title or content is empty
        # NOTE: Have to be more specific
        if (request.form['title'] == '') or (request.form['content'] == ''):
          raise Exception()

        if('required_chapters[]' in request.form):
          required_list = []
          # Add required chapter from the form
          for required_chapter in request.form.getlist('required_chapters[]'):
            required = sess.query(Chapter).filter_by(chapter_id=required_chapter).one()
            required_list.append(required)
          chapter.required_chapters = required_list
        sess.add(chapter)
        sess.commit()
        flash('Chapter has been updated', 'success')
        return redirect(url_for('admin_index'))
      except Exception, e:
        # Roll the transaction back
        sess.rollback()
        # Add flash by checking all possible cause that raise the exception
        if request.form['title'] == '':
          flash("Title can't be blank", 'error')
        elif request.form['content'] == '':
          flash("Content can't be blank", 'error')
        elif 'chapters_pkey' in e.message:
          flash('Chapter number is duplicate', 'error')
        else:
          # Because now an exception isn't specific
          # so we raise it if we don't know what it is
          raise e

        # Render a template with previous form data is filled
        return render_template('admin/chapters/edit.html',
                              area='chapter/edit',
                              unescape=unescape, 
                              chapter=request.form,
                              chapters=chapters,
                              required_chapters=required_chapters)
  except exc.NoResultFound, e:
    flash('Unable to find given chapter id')
    return redirect(url_for('admin_index'))

@app.route('/admin/chapters/delete/<string:chapter_id>')
@require_admin_auth
def admin_chapter_delete(chapter_id):
  sess = Session()
  try:
    chapter = sess.query(Chapter).filter_by(chapter_id=chapter_id).one()
    sess.delete(chapter)
    sess.commit()
    flash('Chapter was deleted')
    return redirect(url_for('admin_index'))
  except exc.NoResultFound, e:
    sess.rollback()
    flash('Unable to find given chapter id')
    return redirect(url_for('admin_index'))
  except Exception, e:
    sess.rollback()
    flash('Unable to delete chapter')
    return redirect(url_for('admin_index'))

@app.route('/admin/questions/')
@require_admin_auth
def admin_question_index():
  sess = Session()
  questions = sess.query(Question).order_by(Question.id).all()
  return render_template('admin/questions/index.html',
                         area='question',
                         questions=questions,
                         unescape=unescape)

@app.route('/admin/questions/new', methods=['POST'])
@require_admin_auth
def admin_question_new():
  sess = Session()
  try:
    question = Question(request.form['question'],
                        request.form['answer'],
                        request.form['type'],
                        request.form['hint'])
    chapter = sess.query(Chapter).filter_by(chapter_id=request.form['chapter_id']).one()
    question.chapter = chapter
    sess.add(question)
    sess.commit()
    if request.is_xhr:
      json_item = jsonify(id=question.id,
                          question=question.question)
      json_item.status_code = 200
      return json_item
    else:
      return redirect(url_for('admin_question_index'))
  except Exception, e:
    sess.rollback()
    json_item = jsonify(message=e.message)
    json_item.status_code = 500
    return json_item

@app.route('/admin/questions/edit/<int:id>', methods=['GET', 'POST'])
@require_admin_auth
def admin_question_edit(id):
  sess = Session()
  try:
    question = sess.query(Question).filter_by(id=id).one()
    if request.method == 'GET':
      return render_template('admin/questions/edit.html',
                             area='question/edit',
                             question=question,
                             unescape=unescape)
    else:
      try:
        question.question = request.form['question']
        question.answer = request.form['answer']
        question.type = request.form['type']
        question.hint = request.form['hint']

        if (request.form['question'] == '') or (request.form['answer'] == ''):
          raise Exception()

        sess.add(question)
        sess.commit()
        flash('Question has been updated', 'success')
        return redirect(url_for('admin_question_index'))
      except Exception, e:
        # Roll the transaction back
        sess.rollback()
        # Add flash by checking all possible cause that raise the exception
        if request.form['question'] == '':
          flash("Question can't be blank", 'error')
        elif request.form['answer'] == '':
          flash("Answer can't be blank", 'error')
        else:
          # Because now an exception isn't specific
          # so we raise it if we don't know what it is
          raise e

        return render_template('admin/questions/edit.html',
                              area='chapter/edit',
                              unescape=unescape, 
                              question=request.form)
  except exc.NoResultFound, e:
    flash('Unable to find given question id')
    return redirect(url_for('admin_question_index'))

@app.route('/admin/questions/delete/<int:id>')
@require_admin_auth
def admin_question_delete(id):
  sess = Session()
  try:
    question = sess.query(Question).filter_by(id=id).one()
    sess.delete(question)
    sess.commit()
    flash('Question was deleted')
    return redirect(url_for('admin_question_index'))
  except Exception, e:
    sess.rollback()
    flash('Unable to delete question')
    return redirect(url_for('admin_question_index'))


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
    if (request.form['username'] == 'admin') and \
    (request.form['password'] == 'admin'):
      session['admin'] = request.form['username']
      return redirect(url_for('admin_index'))
  return render_template('admin/login.html')

@app.route('/admin/logout/')
def admin_logout():
  session.pop('admin', None)
  return redirect(url_for('admin_login'))