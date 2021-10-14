from flask import Blueprint, render_template

from .forms import LoginForm


admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

# 'admin' имя блупринта, будет суффиксом ко всем именам методов данного модуля
# __name__ - имя исполняемого модуля, относительно которого будет искаться папка admin и соответствующие подкаталоги
# 

@admin.route("/")
def index():
    return render_template("index.html", title="Про Flask")

# в redirect(url_for('.index')) с точкой index будет искаться в текущем приложении admin, или можно указать admin.index, admin - первый параметр в Blueprint()


@admin.route("/login", methods=("POST", "GET"))
def login():
    form = LoginForm()

    if form.validate_on_submit(): # validate_on_submit - были ли отправлены в этой форме какие-либо данные POST - запросом
        # эквивалент if request.method == "POST", а также проверяет корректность введенных данных в соответствии с validators
        print(form.email.data)
        return render_template("admin/login.html", title="Про Flask", form=form)
    return render_template("admin/login.html", title="Про Flask", form=form)


@admin.route("/register",  methods=("POST", "GET"))
def register():
    form = LoginForm()

    if form.validate_on_submit(): 
        print(form.email.data)
        return render_template("admin/login.html", title="Про Flask", form=form)
    return render_template("admin/login.html", title="Про Flask", form=form)
