import os
import sqlite3
from sqlite3.dbapi2 import connect

from flask import Flask, render_template, sessions, url_for, request, flash, session, redirect, abort, g, make_response
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_manager, login_user, login_required # login_required декоратор для ограничения доступа

from UserLogin import UserLogin

# url_for - генерирует url в соответстви с переданной функцией url_for(about)
# функция url_for работает только в пределах контекста запроса
# url_for('user', username='somename') для использования url с параметрами
# flash - отправляет сообщения которые доступные в форме, использует сессии

# Декораторы перехвата запросов 
# before_first_request - выполняет ф-ю до обработки первого запроса
# before_request - выполняет ф-ю до обработки первого запроса
# after_request - выполняет ф-ю после обработки запроса (не вызввается при возникновениии исключений в обработчике запросов)
# teardown_request - всегда выполняет ф-ю после обработки запроса

# set_cookie(key, value="", max_age=None) 
# key - название куки, value - данные хранящиеся под указанным ключом, max_age - время хранения

# generate_password_hash() - выполняет кодирование строки данных по стандарту PBKDF2
# check_password_hash() - выполняет проверку указанных данных на соответствие хеша


app = Flask(__name__)

SECRET_KEY = 'jfnvkjnrkjv'  # для шифрования сессий в браузере пользователя
DATABASE  = '/tmp/flsite.db'
DEBUG = True

app.config.from_object(__name__) # загрука кофигурации
# альтернативный вариант указания конфигурации app.config['SECRET_KEY'] = 'jfnvkjnrkjv'

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login' # для перехода в случае если пользователь не авторизован
login_manager.login_message = 'Авторизуйтесь для доступа к закрытым страницам' # для добавления мгновенного сообщения

@login_manager.user_loader
def load_user(user_id):
    print('load user')
    return UserLogin().fromDB(user_id, dbase=None)

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row # данные из БД будут представленны в виде словаря
    return conn

def create_db():
    """Вспомогательная функция для создания БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    """Соединение с БД, если не устаовлено"""
    if not hasattr(g, 'link_db'): # g - глобальная переменная из контекста приложения
        g.link_db = connect_db()
    return g.link_db


menu = [{"name": "Установка", "url": "install-flask"},
        {"name": "Обратная связь", "url": "contact"}]
 
@app.route("/index") # один обработчик обрабатывает два адреса
@app.route("/")
# создается контекст запроса
def index():
    
    # для работы с заголовками
    # content = render_template("index.html", title="Про Flask",  menu=menu)
    # res = make_response(content, 200)
    # res.headers['Content-Type'] = 'text/text' # должно соответствовать данным которые передаются браузером
    # res.headers['Server'] = 'flasksite'
    # return res

    
    session.permanent = True # в таком случае время жизни сессии 31 день, для изменения явно указать app.permanent_session_lifetime=datatime
    if 'visits' in session: 
        # данные сессий передаются клиенту только если они меняются, 
        # session['data'] = [1, 2], session['data'][1] += 1 - передаваться не будет. Для передачи нужно указать session.modified = True
        session['visits'] = session.get('visits') + 1
    else:
        session['visits'] = 1
    return render_template("index.html", title="Про Flask", visits=session['visits'],  menu=menu)


@app.route("/transfer")
def transfer():
    return redirect(url_for('index'), 301) # использование перенаправления

@app.route("/cookies")
def cookies():
    log = ''
    if request.cookies.get('logged'):
        log = request.cookies.get('logged')
    content = render_template("index.html", log=log,  menu=menu)
    res = make_response(content)
    res.set_cookie("logged", "yes") # для удаления  res.set_cookie("logged", "", 0)
    return res

@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Cooбщение отправлено!', category='success')
        else:
            flash('Ошибка отправки!', category='error')
        print(request.form)

    return render_template("contact.html", menu=menu) # about.html берется из templates которая находится относительно рабочего каталога

@app.route("/login", methods=["POST", "GET"])
def login():
    # user получен из бд
    # userlogin = UserLogin().create(user)
    # login_user(userlogin)
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == 'admin' and request.form['password'] == "123":
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template("login.html",  menu=menu)

@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'User {username}'


@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return f'Post {post_id}'

@app.route('/anypath/<path:subpath>') # конвертер path - говорит о том, что всё что после anypath нужно поместить в переменную subpath
def show_subpath(subpath):
    # show the subpath after /path/
    return f'Subpath {escape(subpath)}'

@app.errorhandler(404) # декоратор обработки ошибок
def pageNotFound(error):
    return render_template('page404.html', title='Страница не найдена', menu=menu), 404


@app.before_request
def before_request():
    db = get_db() #  установка соединения с бд
    print('Connection to db establish')



@app.teardown_appcontext # срабатывает когда когда происходит уничтожение контекста приложения
def close_db(response):
    """Закрываем соединение с БД, если установлено"""
    if hasattr(g, 'link_db'):
        g.link_db.close()

if __name__ == "__main__":
    app.run(debug=True)
