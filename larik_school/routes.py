from flask import render_template, url_for, request, redirect, flash, session, abort, jsonify
from larik_school.forms import RegistationForm, LoginForm, LessonsForm, ProblemForm, CategoryForm
from larik_school.models import Task, User, Event, Lesson, Problem, Category
from larik_school import app, db, bcrypt
from datetime import datetime
from hashlib import md5
from flask_login import login_user, current_user, logout_user, login_required
import os

SALT = 'JAKLDFJ@ajsflj(@kdsf@@@!19435f)'
import json




def format_date(datetime):
    return f'{str(datetime.day).zfill(2)}.{str(datetime.month).zfill(2)}.{datetime.year} {str(datetime.hour).zfill(2)}:{str(datetime.minute).zfill(2)}'

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'GET':
        tasks = Task.query.filter(Task.user_id==current_user.id).all()
        for task in tasks:
            task.datetime = format_date(task.datetime)
        return render_template('index.html', tasks=tasks)
    else:
        try:
            new_task = Task(content=request.form["content"],user_id=current_user.id)
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
        user = User.query.filter(User.email==email).first()    
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
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
@login_required
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
@login_required
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
@login_required
def editEventDate():
    data = request.form.to_dict()
    event = Event.query.filter(Event.id == data['id'])
    event.update({'start':datetime.strptime(data['start'], '%Y-%m-%d %H:%M:%S'), 'end':datetime.strptime(data['end'], '%Y-%m-%d %H:%M:%S')})
    db.session.commit()
    return 'OK'
@app.route('/logout')
def logout():
    logout_user()
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
            new_lesson = Lesson(title=form.title.data, content=form.content.data, user_id=current_user.id)
            db.session.add(new_lesson)
            db.session.commit()
            flash('Урок добавлен', 'success')
            return redirect(url_for('lessons'))
@app.route('/author/<int:author_id>')
def author(author_id):
    user = User.query.get(author_id)
    return render_template('author.html',user=user)

@app.route('/account')
@login_required
def account():
    return f'Страница аккаунта {current_user.username}'



@app.route('/problem/add', methods=['POST', 'GET'])
@login_required
def add_problem():
    basedir = os.path.abspath(os.path.dirname(__file__))
    form = ProblemForm()
    categories = Category.query.all()
    form.category.choices = [(category.id,category.title) for category in categories] 
    filename = None
    if form.validate_on_submit(): 
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':  
                filename = file.filename
                file.save(os.path.join(basedir,'static','imgs', filename))
        if filename:
            new_problem = Problem(question=form.question.data, answer=form.answer.data,img=filename, category_id=form.category.data)
        else:
            new_problem = Problem(question=form.question.data, answer=form.answer.data, category_id=form.category.data)
        db.session.add(new_problem)
        db.session.commit()
        flash('Вопрос добавлен в базу!', 'info')
        return redirect(url_for('tasks'))           
    return render_template('add_problem.html',form=form)

@app.route('/problem/delete/<problem_id>')
def problem_delete(problem_id):
    problem = Problem.query.get(int(problem_id))
    db.session.delete(problem)
    db.session.commit()
    return redirect(url_for('test'))

@app.route('/problem/edit/<problem_id>', methods=['POST', 'GET'])
def problem_edit(problem_id):
    problem = Problem.query.get(int(problem_id))
    basedir = os.path.abspath(os.path.dirname(__file__))
    form = ProblemForm()
    categories = Category.query.all()
    form.category.choices = [(category.id,category.title) for category in categories] 
    if form.validate_on_submit(): 
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':  
                filename = file.filename
                file.save(os.path.join(basedir,'static','imgs', filename))
                problem.img = filename
        problem.question = form.question.data
        problem.question = form.question.data
        problem.answer = form.answer.data
        db.session.commit()
        flash('Вопрос отредактирован!', 'info')
        return redirect(url_for('test'))   
    form.question.data = problem.question
    form.answer.data = problem.answer  
    form.category.data = problem.category_id      
    return render_template('add_problem.html',form=form)






@app.route('/tasks', methods=['POST', 'GET'])
def tasks():
    problems = []
    try:
        if request.method == 'POST':
            if 'problem_id' in  request.form:
                problem = Problem.query.get(int(request.form['problem_id']))
                if not problem:
                    raise ValueError
                problems = [problem]
            if 'category_id' in request.form:
                problems = Problem.query.filter_by(category_id=int(request.form['category_id'])).all()
    except:
        problems = []
    categories = Category.query.all()
    return render_template('tasks.html', problems=problems, categories=categories)

@app.route('/check_answer', methods=['POST', 'GET'])
def check_answer():
    guess = request.form['answer']
    problem_id = request.form['problem_id']
    problem = Problem.query.get(int(problem_id))
    answer = problem.answer
    return  str(answer.lower() == guess.lower())


@app.route('/category', methods=['GET', 'POST'])
def category():
    categories = Category.query.all()
    form = CategoryForm()
    if form.validate_on_submit():
        try:
            new_category = Category(title=form.title.data)
            db.session.add(new_category)
            db.session.commit()
            return redirect(url_for('category'))
        except:
            return 'Ошибка записи в БД'   
    return render_template('category.html', form=form, categories=categories)

@app.route('/category/<int:category_id>/delete')
def delete_category(category_id):
    category = Category.query.get(category_id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('category'))

@app.route('/get_problem', methods=['POST', 'GET'])
def get_problem():
    problem_id = request.form['task_number']
    problem = Problem.query.get(int(problem_id))
    return problem.question

@app.route('/create/variant', methods=['GET', 'POST'])
@login_required
def varian_create():
    categories = Category.query.all()
    tasks = []
    if request.method == 'POST':
        for key in request.form:
            if request.form[key].isdigit():
                category_id = int(key)
                tasks.extend(Problem.query.filter_by(category_id=category_id).limit(request.form[key]))
    return render_template('add_variant.html', categories=categories, problems=tasks)

