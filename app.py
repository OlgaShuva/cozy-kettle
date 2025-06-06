from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'ваш-секретный-ключ'

# Инициализация БД
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Модель пользователя
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)

# Загрузчик пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Главные маршруты
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/account')
@login_required
def account():
    return render_template('account.html', user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('account'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')

        if User.query.filter_by(username=username).first():
            flash('Это имя пользователя уже занято', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Этот email уже используется', 'error')
        else:
            user = User(username=username, email=email, phone=phone, address=address)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('account'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('account'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('account'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Для статических файлов
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Для прямого открытия HTML файлов
@app.route('/<page>.html')
def html_pages(page):
    if page in ['index', 'menu', 'account', 'login', 'register']:
        return render_template(f'{page}.html')
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

from models import User
