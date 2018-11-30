from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User
import os

#  region main
@app.route('/')
@app.route('/index')
#@login_required
def index():
    return render_template("index.html", title='Home Page')
#  endregion

# region General
@app.route('/general')
def general():
    return render_template("General/general.html", title='General Page')

#endregion

#  region App
@app.route('/app')
def app_team():
    return render_template("App/app_team.html", title='App Page')


@app.route('/email_template', methods=['GET', 'POST'])
#@login_required
def email_template():
    if current_user.is_anonymous or current_user.department not in ['app']:
        return redirect(url_for('app_team'))
    return render_template("App/email_template.html", title='Email Template')

@app.route('/register', methods=['GET', 'POST'])
#@login_required
def register():
    if current_user.is_anonymous or current_user.department not in ['app']:
        return redirect(url_for('app_team'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, department=form.department.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('App/register.html', title='Register', form=form)
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




