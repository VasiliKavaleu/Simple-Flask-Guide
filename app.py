from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash

from admin.admin import admin # импортируем переменную блупринт


app = Flask(__name__)

app.config['SECRET_KEY'] = 'jfnvkjnrkjv'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
# postgresql://user:password@localhost/mydatabase
# mysql://user:password@localhost/mydatabase
# oracle://user:password@127.0.0.1:1521/mydatabase

app.register_blueprint(admin, url_prefix='/admin') # регистрация блупринта, будет доступен по: домен/<url_prefix>/<URL-blueprint>

db = SQLAlchemy(app)



menu = [{"name": "Установка", "url": "install-flask"},
        {"name": "Обратная связь", "url": "contact"}]


class Users(db.Model):
    """
    Получение всех данныйх - Users.query.all()
    Получение первой записи - Users.query.first()
    Фильтрация 1 - Users.query.filter_by(id=2).all()
    Фильтрация 2 - Users.query.filter(Users.id == 2).all()
    Сортировка - Users.query.order_by(Users.email).all()
    Сортировка по убыванию - Users.query.order_by(Users.email.desc()).all()
    Простое получение пользователя для получения первичного ключа - Users.query.get(2)

    Выборка из двух таблиц:
    res = db.session.query(Users, Profiles).join(Profiles, User.id == Profiles.user_id).all()

    Обращаемся к переменной db которая ссылается на класс SQLAlchemy,
    затем через сессию орбащаемся к методу query и указываем таблицы которые будем выбирать по данному запросу
    (Users, Profiles) - записи из этих таблиц следует объединить используя id из таблицы Users и user_id из Profiles
    при чем записи таблицы Profiles будут добавляться к таблице Users, как буд-то Users главная, а Profiles вспомогательная
    из которой подключаются дополнительные записи согласно условию и далее говорим, что хотим выбрать все такие записи all()

    В таблице с первичными данными (Users) можно прописать специальную переменную:
    pr = db.relationship('Profiles', backref='users', uselist=False)

    Через эту переменную будет устанавливаться связь с таблицей Profiles по внешнему ключу user_id,
    users - какую таблицу присоединять к Profiles, uselist - соответствует тому, что одной записи из
    таблици Users должна соответствовать одна запись из таблицы Profiles
    """

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    pr = db.relationship('Profiles', backref='users', uselist=False)

    def __repl__(self):
        return f"<users {self.id}>"


class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    old = db.Column(db.Integer)
    city = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repl__(self):
        return f"<users {self.id}>"


@app.route("/")
def index():
    return render_template("index.html", title="Про Flask",  menu=menu)

@app.route('/register', methods=("POST", "GET"))
def register():
    if request.method == "POST":

        # проверка на корректность введенных данных

        try:
            hash = generate_password_hash(request.form['password'])
            u = Users(email=request.form['password'], psw=hash)
            db.session.add(u) # запись хранится в сессии, в памяти устройства, фактически в таблицу не занесена
            db.session.flush() # из сесии перемещает запись в таблицу, но все изменения происходят в памяти устройства

            u = Profiles(name=request.form['name'], old=request.form['old'],
                        city=request.form['city'], user_id=u.id) # из памяти в таблице помещенны с помощью команды db.session.flush()
            db.session.add(u) 
            db.session.commit() # физически меняет БД и применяет изменения в таблице
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

    return render_template("register.html",  menu=menu)


@app.route("/login", methods=["POST", "GET"])
def login():
    return render_template("login.html",  menu=menu)


if __name__ == "__main__":
    app.run(debug=True)
