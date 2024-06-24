from flask import Flask, render_template, url_for, request, redirect, flash, session, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashlib import md5
SALT = 'JAKLDFJ@ajsflj(@kdsf@@@!19435f)'
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///task.db"
app.config["SECRET_KEY"] = 'daflkjie25kj3l1k'
db = SQLAlchemy(app)

def format_date(datetime):
    return f'{str(datetime.day).zfill(2)}.{str(datetime.month).zfill(2)}.{datetime.year} {str(datetime.hour).zfill(2)}:{str(datetime.minute).zfill(2)}'
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f"Task {self.id}: {self.content}"
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    color = db.Column(db.String)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)

    def to_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns} 
    



with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'userLogged' not in session:
        return redirect(url_for('login'))
    if request.method == 'GET':
        tasks = Task.query.filter(Task.user_id==session.get('userId')).all()
        for task in tasks:
            task.datetime = format_date(task.datetime)
        return render_template('index.html', tasks=tasks)
    else:
        try:
            new_task = Task(content=request.form["content"],user_id=session['userId'])
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'Ошибка сохранения в БД'

@app.route('/delete/<int:task_id>')
def task_delete(task_id):
    task = Task.query.filter(Task.id==task_id, Task.user_id==session.get('userId'))
    task.delete()
    db.session.commit()
    return redirect('/')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'userLogged' in session:
        return redirect(url_for('index'))
    elif request.method=="POST":
        name = request.form['username'] 
        password_hash = md5((request.form['password'] + SALT).encode()).hexdigest()
        user = User.query.filter(User.username==name, User.password==password_hash).first()
        if user:
            session['userLogged'] = user.username
            session['userId'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Такой пользователь не найден! Проверьте логин и пароль!', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method=="POST":
        password = request.form['password']
        password2 = request.form['password2']
        user = request.form['username']
        errors = []
        if len(password) < 6:
            errors.append('Длина пароля меньше 6 символов!')
        if password != password2:
            errors.append('Пароль и подтверждение не совпадают!')
        have_digit = False
        have_lower_case_letters = False
        have_upper_case_letters = False
        for letter in password:
            if letter.isdigit():
                have_digit = True
            if (letter.isalpha()):
                if letter.isupper():
                    have_upper_case_letters = True
                else:
                    have_lower_case_letters = True
        if not have_digit:
            errors.append('Пароль должен содержать цифры')
        if not have_lower_case_letters:
            errors.append('Пароль должен содержать буквы в нижнем регистре!')
        if not have_upper_case_letters:
            errors.append('Пароль должен содержать буквы в верхнем регистре!')
        for error in errors:
            flash(error,'error')
        if not errors:
            # try:
            new_user=User(username=user, password=md5((password + SALT).encode()).hexdigest())
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация прошла успешно!','info')
            return redirect(url_for('login'))
            # except:
            #     return 'Что-то пошло не так!'
    return render_template('signup.html')

@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    if request.method == 'POST':
        title = request.form['title']
        color = request.form['color']
        start = datetime.strptime(request.form['start'], '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(request.form['end'], '%Y-%m-%d %H:%M:%S')
        new_event = Event(title=title, color=color, start=start, end=end)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('calendar'))
    else:
        items = Event.query.all()
        events = [item.to_dict() for item in items]
        for event in events:
            date_el, time_el = event['start'].split()
            if time_el == '00:00:00':
                event['start'] = date_el 
            date_el, time_el = event['end'].split()
            if time_el == '00:00:00':
                event['end'] = date_el
        print('Это содержимео events', events )
        return render_template('calendar.html', events=events)
    

@app.route('/editEvent', methods=['POST'])
def editEvent():
    id = request.form['id']
    title = request.form['title']
    color = request.form['color']
    event = Event.query.filter(Event.id == id)
    if 'delete' in request.form:
        event.delete()
    else:
        event.update({'title':title, 'color':color})
    db.session.flush()
    db.session.commit()
    return redirect(url_for('calendar'))
@app.route('/editEventDate', methods=['POST'])
def editEventDate():
    data = request.form.to_dict()
    event = Event.query.filter(Event.id == data['id'])
    event.update({'start':datetime.strptime(data['start'], '%Y-%m-%d %H:%M:%S'), 'end':datetime.strptime(data['end'], '%Y-%m-%d %H:%M:%S')})
    db.session.commit()
    return 'OK'
@app.route('/logout')
def logout():
    session.pop('userLogged', None)
    session.pop('userId', None)
    return redirect(url_for('index'))
@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html')

if __name__ == '__main__':
    app.run(debug=True)


