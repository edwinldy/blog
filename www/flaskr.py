#all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = './tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)
# from_object() 会查看给定的对象（如果该对象是一个字符串就会 直接导入它），搜索对象中所有变量名均为大字字母的变量。在我们的应用中，已经将配 置写在前面了。你可以把这些配置放到一个独立的文件中。
# from_object() 一行替换为:

# app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# 这样做就可以设置一个 FLASKR_SETTINGS 的环境变量来指定一个配置文件，并 根据该文件来重载缺省的配置。 silent 开关的作用是告诉 Flask 如果没有这个环境变量 不要报错。

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db) as db:
        with app.open_resource('scheme.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    g.db.close()

# 这个视图会把条目作为字典传递给 show_entries.html 模板，并返回渲染结果:
@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

# 这个视图可以让一个登录后的用户添加一个新条目。本视图只响应 POST 请求，真正的 表单显示在 show_entries 页面中。如果一切顺利，我们会 flash() 一个消息给下一个请求并重定向回到 show_entries 页面:
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries(title, text) values (?, ?)', [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

# 这些函数用于用户登录和注销。登录视图根据配置中的用户名和密码验证用户并在会话中 设置 logged_in 键值。如果用户通过验证，键值设为 True ，那么用户会被重定向到 show_entries 页面。另外闪现一个信息，告诉用户已登录成功。如果出现错误，模板会 提示错误信息，并让用户重新登录:
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

# 登出视图则正好相反，把键值从会话中删除。在这里我们使用了一个小技巧：如果你使用 字典的 pop() 方法并且传递了第二个参数（键的缺省值），那么当字典中有 这个键时就会删除这个键，否则什么也不做。这样做的好处是我们不用检查用户是否已经 登录了。
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run(host='0.0.0.0') #host='0.0.0.0'告诉你的操作系统监听一个公开的 IP 。