from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model for login system
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    deadline = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default="Pending")
    subtask = db.Column(db.String(200), nullable=True)
    reminder_time = db.Column(db.String(20), nullable=True)

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
@login_required
def add():
    task_name = request.form['task']
    priority = request.form['priority']
    category = request.form['category']
    deadline = request.form['deadline']
    subtask = request.form.get('subtask', '')
    reminder_time = request.form.get('reminder_time', '')
    new_task = Task(name=task_name, priority=priority, category=category, deadline=deadline, subtask=subtask, reminder_time=reminder_time)
    db.session.add(new_task)
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')

@app.route('/complete/<int:id>')
@login_required
def complete(id):
    task = Task.query.get(id)
    task.status = "Completed"
    db.session.commit()
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Checking if the username and password match
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash("Login Successful!", "success")
            return redirect('/')
        else:
            flash("Invalid credentials. Please try again.", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out successfully.", "info")
    return redirect('/login')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database is created
        # Check if there is no user in the database and add a default one if so
        if not User.query.filter_by(username="admin").first():  # Check if a user already exists with the username 'admin'
            default_user = User(username="admin", password="admin123")  # Default username and password
            db.session.add(default_user)
            db.session.commit()  # Save the default user to the database
    app.run(debug=True)
