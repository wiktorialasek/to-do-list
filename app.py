# from flask import Flask, render_template, redirect, url_for, flash, Blueprint
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from forms import LoginForm, RegisterForm
# from werkzeug.security import check_password_hash, generate_password_hash
# from datetime import timedelta
# from functools import wraps
# from flask import abort
# import os

# app = Flask(__name__)
# app.config['SECRET_KEY'] = os.urandom(24) 
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Czas trwania sesji

# db = SQLAlchemy(app)
# login_manager = LoginManager() #implementuje moduł logowania 
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(150), unique=True, nullable=False)
#     password = db.Column(db.String(150), nullable=False)
#     role = db.Column(db.String(50), nullable=False, default='user')

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# def role_required(role):
#     def decorator(func):
#         @wraps(func)
#         def decorated_view(*args, **kwargs):
#             if not current_user.is_authenticated or current_user.role != role:
#                 abort(403)
#             return func(*args, **kwargs)
#         return decorated_view
#     return decorator

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegisterForm()
#     if form.validate_on_submit():
#         hashed_password = generate_password_hash(form.password.data, method='pbkdf2')
#         new_user = User(username=form.username.data, password=hashed_password, role=form.role.data)
#         db.session.add(new_user)
#         db.session.commit()
#         return redirect(url_for('login'))
#     return render_template('register.html', form=form)

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user and check_password_hash(user.password, form.password.data):
#             login_user(user, remember=form.remember.data)
#             if user.role == 'admin':
#                 return redirect(url_for('admin_dashboard'))
#             else:
#                 return redirect(url_for('dashboard'))
#         flash('Invalid username or password')
#     return render_template('login.html', form=form)

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     return f'Hello, {current_user.username}!'

# @app.route('/admin.dashboard')
# @login_required
# def admin_dashboard():
#     return f'Hello Admin, {current_user.username}!'

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('login'))

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)

from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegisterForm
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def role_required(role):
    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return func(*args, **kwargs)
        return decorated_view
    return decorator

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2')
        new_user = User(username=form.username.data, password=hashed_password, role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.username}!'

@app.route('/adashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    # Display the full admin page content here
    return render_template('admin_dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

