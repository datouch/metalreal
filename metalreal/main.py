from metalreal import app
from flask import session, redirect, url_for, render_template, request

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
    return render_template('admin/index.html')

@app.route('/admin/chapters/new')
def admin_chapter_new():
    return render_template('admin/chapter.new.html')

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
