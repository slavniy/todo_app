from flask import render_template, url_for, request, redirect, flash, session, abort, jsonify
from larik_school.forms import RegistationForm, LoginForm, LessonsForm
from larik_school.models import Task, User, Event, Lesson
from larik_school import app, db, bcrypt
from datetime import datetime
from hashlib import md5

SALT = 'JAKLDFJ@ajsflj(@kdsf@@@!19435f)'
import json




def format_date(datetime):
    return f'{str(datetime.day).zfill(2)}.{str(datetime.month).zfill(2)}.{datetime.year} {str(datetime.hour).zfill(2)}:{str(datetime.minute).zfill(2)}'

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
    form = LoginForm()
    if 'userLogged' in session:
        return redirect(url_for('index'))
    elif form.validate_on_submit():
        email = form.email.data
        password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User.query.filter(User.email==email, User.password==password_hash).first()
        if user:
            session['userLogged'] = user.username
            session['userId'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Такой пользователь не найден! Проверьте логин и пароль!', 'error')
    return render_template('login.html', form=form)


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegistationForm()
    if form.validate_on_submit():
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user=User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash(f'Регистрация пользователя {form.username.data} прошла успешно!','info')
            return redirect(url_for('login'))
        except:
            return 'Ошибка при записи пользователя в БД!'
    return render_template('register.html', form=form)


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

@app.route('/lessons', methods=['GET', 'POST'])
def lessons():
    form = LessonsForm()
    if request.method=='GET':
        lessons = Lesson.query.all()
        for lesson in lessons:
            print(lesson.author)
        return render_template('lessons.html', lessons=lessons, form=form)
    else:
        if form.validate_on_submit():
            new_lesson = Lesson(title=form.title.data, content=form.content.data, user_id=session['userId'])
            db.session.add(new_lesson)
            db.session.commit()
            flash('Урок добавлен', 'success')
            return redirect(url_for('lessons'))
@app.route('/author/<int:author_id>')
def author(author_id):
    user = User.query.get(author_id)
    return render_template('author.html',user=user)