from app import app, db
from app.forms import LoginForm, RegistrationForm, EditUserForm, deptList, DBRegistrationForm, BatchSendEmailForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User, Database
import pyodbc
import json
from app.email import send_email

#  region main
@app.route('/')
@app.route('/index')
#@login_required
def index():
    return render_template("index.html", title='Home Page')
#  endregion

# region Admin
@app.route('/admin')
def admin():
    if current_user.is_anonymous:
        return redirect(url_for('index'))
    return render_template("Admin/admin.html", title='Admin Page')

@app.route('/db_management', methods=['GET', 'POST'])
def db_management():
    if current_user.is_anonymous:
        return redirect(url_for('index'))
    if current_user.department not in ['admin']:
        return redirect(url_for('index'))
    dbs = Database.query.all()
    #departments = SelectField('Department',coerce=str, choices=deptList, default=1)
    return render_template("Admin/db_management.html", title='DB Management', dbs=dbs)

@app.route('/register_db', methods=['GET', 'POST'])
@login_required
def register_db():
    if current_user.is_anonymous or current_user.department not in ["admin"] :
        return redirect(url_for('index'))
    form = DBRegistrationForm()

    if form.validate_on_submit():
        new_db = Database(driver=form.driver.data, host=form.host.data, db_name=form.db_name.data
                      ,login=form.login.data, remark=form.remark.data)
        new_db.set_password(form.password.data)
        db.session.add(new_db)
        db.session.commit()
        flash('Congratulations, you have successfully registered a database!')
        return redirect(url_for('db_management'))

    return render_template('Admin/register_db.html', title='Register DB', form=form)

@app.route('/delete_db', methods=['POST'])
@login_required
def delete_db():
    if current_user.is_anonymous or current_user.department not in ["admin"] :
        return redirect(url_for('index'))
    try:
        dbid = request.form['dbid']
        each_db = Database.query.filter_by(id=dbid).first()
        if each_db is None:
            flash('Invalid Database')
            return redirect(url_for('db_management'))
        db.session.delete(each_db)
        db.session.commit()
        return redirect(url_for('db_management'))
    except Exception as e:
        return render_template('Errors/error.html', error=str(e))

@app.route('/test_db', methods=['POST'])
@login_required
def test_db():
    if current_user.is_anonymous or current_user.department not in ["admin"] :
        return redirect(url_for('index'))
    try:
        dbid = request.form['dbid']
        each_db = Database.query.filter_by(id=dbid).first()
        if each_db is None:
            flash('Invalid Database')
            return redirect(url_for('db_management'))
        msg = '{} is not Connected!'.format(each_db.remark)
        try:
            conn = pyodbc.connect('driver={%s};server=%s;database=%s;uid=%s;pwd=%s' % (each_db.driver, each_db.host, each_db.db_name, each_db.login, each_db.get_password()), timeout=3)
        except:
            pass

        if conn:
            msg = "Connection Successful!"
        result = []
        result.append({'result': msg})
        return json.dumps(result)
    except Exception as e:
        return render_template('Errors/error.html', error=str(e))

@app.route('/user_management', methods=['GET', 'POST'])
def user_management():
    if current_user.is_anonymous:
        return redirect(url_for('index'))
    if current_user.department not in ['admin']:
        return redirect(url_for('index'))
    users = User.query.all()
    #departments = SelectField('Department',coerce=str, choices=deptList, default=1)
    return render_template("Admin/user_management.html", title='User Management', users=users)


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.is_anonymous or current_user.department not in ["admin"] :
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, department=form.department.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you have successfully registered a user!')
        return redirect(url_for('user_management'))

    return render_template('Admin/register_user.html', title='Register User', form=form)

@app.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    if current_user.is_anonymous or current_user.department not in ["admin"] :
        return redirect(url_for('index'))
    try:
        userid = request.form['userid']
        user = User.query.filter_by(id=userid).first()
        if user is None:
            flash('Invalid username or password')
            return redirect(url_for('user_management'))
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('user_management'))
    except Exception as e:
        return render_template('Errors/error.html', error=str(e))


@app.route('/edit_user', methods=['POST'])
@login_required
def edit_user():
    if current_user.is_anonymous or current_user.department not in ["admin"] :
        return redirect(url_for('index'))
    try:
        userid = request.form['userid']
        username = request.form['username']
        department = request.form['department']
        editUser = []
        editUser.append({'username': username,'department': department, 'userid': userid})
        return json.dumps(editUser)
    except Exception as e:
        return render_template('Errors/error.html', error=str(e))

@app.route('/edit_user_update', methods=['POST'])
@login_required
def edit_user_update():
    if current_user.is_anonymous or current_user.department not in ["admin"] :
        return redirect(url_for('index'))
    try:
        id = request.form['update_user_id']
        username = request.form['update_user']
        department = request.form['update_department']
        password = request.form['update_user_password']
        user = User.query.filter_by(id=id).first()
        if user is None or username == '':
            flash('Invalid username or password')
            return redirect(url_for('user_management'))
        user.username = username
        user.department = department
        if password != '':
            user.set_password(password)
        db.session.commit()
        return redirect(url_for('user_management'))
    except Exception as e:
        return render_template('Errors/error.html', error=str(e))

#endregion

#  region App
@app.route('/app')
def app_team():
    return render_template("App/app_team.html", title='App Page')


@app.route('/batch_send_email', methods=['GET', 'POST'])
@login_required
def batch_send_email():
    if current_user.is_anonymous or current_user.department not in ['admin','app']:
        return redirect(url_for('index'))
    form = BatchSendEmailForm()

    recipients = []

    if form.validate_on_submit():
        recipients.append(form.recipient.data)
        send_email(subject=form.sender_name.data + '-' + form.subject.data
                   , sender=form.sender.data
                   , recipients=recipients
                   , text_body="Hello World!"
                   , attach=form.attach.data)
        flash('Email Sent to ' + form.recipient.data)
        return redirect(url_for('batch_send_email'))
    return render_template("App/batch_send_email.html", title='Email', form=form)

#  endregion

# region Operation
@app.route('/operations')
def operations():
    return render_template("Operations/operations.html", title='Operation Page')


#  endregion

#  region about
@app.route('/about')
#@login_required
def about():
    return render_template("about.html", title='About Page')
#  endregion

#  region login/out
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        # deal with @login_required
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
#  endregion




