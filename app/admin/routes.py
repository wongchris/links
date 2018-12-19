from app import db
from app.models import User, Database
from app.admin.forms import DBRegistrationForm, RegistrationForm, TestForm
from flask import render_template, flash, redirect, url_for, request,send_file, Response
from flask_login import current_user, login_required
import pyodbc
import json
import pandas as pd
from io import BytesIO
from app.admin import bp


@bp.route('/admin')
def admin():
    if current_user.is_anonymous:
        return redirect(url_for('main.index'))
    return render_template("admin/admin.html", title='admin Page')

@bp.route('/db_management', methods=['GET', 'POST'])
def db_management():
    if current_user.is_anonymous:
        return redirect(url_for('main.index'))
    if current_user.department not in ['admin']:
        return redirect(url_for('main.index'))
    dbs = Database.query.all()
    #departments = SelectField('Department',coerce=str, choices=deptList, default=1)
    return render_template("admin/db_management.html", title='DB Management', dbs=dbs)

@bp.route('/register_db', methods=['GET', 'POST'])
@login_required
def register_db():
    if current_user.is_anonymous or current_user.department not in ["admin"] :
        return redirect(url_for('main.index'))
    form = DBRegistrationForm()

    if form.validate_on_submit():
        new_db = Database(driver=form.driver.data, host=form.host.data, db_name=form.db_name.data
                      ,login=form.login.data, remark=form.remark.data)
        new_db.set_password(form.password.data)
        db.session.add(new_db)
        db.session.commit()
        flash('Congratulations, you have successfully registered a database!')
        return redirect(url_for('admin.db_management'))

    return render_template('admin/register_db.html', title='Register DB', form=form)

@bp.route('/delete_db', methods=['POST'])
@login_required
def delete_db():
    if current_user.is_anonymous or current_user.department not in ["admin"] :
        return redirect(url_for('main.index'))
    try:
        dbid = request.form['dbid']
        each_db = Database.query.filter_by(id=dbid).first()
        if each_db is None:
            flash('Invalid Database')
            return redirect(url_for('admin.db_management'))
        db.session.delete(each_db)
        db.session.commit()
        return redirect(url_for('admin.db_management'))
    except Exception as e:
        return render_template('errors/error.html', error=str(e))

@bp.route('/test_db', methods=['POST'])
@login_required
def test_db():
    if current_user.is_anonymous or current_user.department not in ["admin"] :
        return redirect(url_for('main.index'))
    try:
        dbid = request.form['dbid']
        each_db = Database.query.filter_by(id=dbid).first()
        if each_db is None:
            flash('Invalid Database')
            return redirect(url_for('admin.db_management'))
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
        return render_template('errors/error.html', error=str(e))

@bp.route('/user_management', methods=['GET', 'POST'])
def user_management():
    if current_user.is_anonymous:
        return redirect(url_for('main.index'))
    if current_user.department not in ['admin']:
        return redirect(url_for('main.index'))
    users = User.query.all()
    #departments = SelectField('Department',coerce=str, choices=deptList, default=1)
    return render_template("admin/user_management.html", title='User Management', users=users)


@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.is_anonymous or current_user.department not in ["admin"] :
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, department=form.department.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you have successfully registered a user!')
        return redirect(url_for('admin.user_management'))

    return render_template('admin/register_user.html', title='Register User', form=form)

@bp.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    if current_user.is_anonymous or current_user.department not in ["admin"] :
        return redirect(url_for('main.index'))
    try:
        userid = request.form['userid']
        user = User.query.filter_by(id=userid).first()
        if user is None:
            flash('Invalid username or password')
            return redirect(url_for('admin.user_management'))
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin.user_management'))
    except Exception as e:
        return render_template('errors/error.html', error=str(e))


@bp.route('/edit_user', methods=['POST'])
@login_required
def edit_user():
    if current_user.is_anonymous or current_user.department not in ["admin"] :
        return redirect(url_for('main.index'))
    try:
        userid = request.form['userid']
        username = request.form['username']
        department = request.form['department']
        editUser = []
        editUser.append({'username': username,'department': department, 'userid': userid})
        return json.dumps(editUser)
    except Exception as e:
        return render_template('errors/error.html', error=str(e))

@bp.route('/edit_user_update', methods=['POST'])
@login_required
def edit_user_update():
    if current_user.is_anonymous or current_user.department not in ["admin"] :
        return redirect(url_for('main.index'))

    id = request.form['update_user_id']
    username = request.form['update_user']
    department = request.form['update_department']
    password = request.form['update_user_password']
    user = User.query.filter_by(id=id).first()
    if user is None or username == '':
        flash('Invalid username or password')
        return redirect(url_for('admin.user_management'))
    user.username = username
    user.department = department
    if password != '':
        user.set_password(password)
    db.session.commit()
    return redirect(url_for('admin.user_management'))


@bp.route('/test_form', methods=['GET', 'POST'])
@login_required
def test_form():
    if current_user.is_anonymous or current_user.department not in ['admin']:
        return redirect(url_for('main.index'))
    form = TestForm()
    print(form.fx_file.data)
    if form.validate_on_submit():
        if not form.fx_file.data:
            flash(message="No FX Rate File Imported!", category='error')
            return redirect(url_for('admin.test_form'))
            # create a random Pandas dataframe

        df_1 = pd.read_excel(form.fx_file.data)

        # create an output stream
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')

        # taken from the original question
        df_1.to_excel(writer, startrow=0, merge_cells=False, sheet_name="Sheet_1")
        #workbook = writer.book
        #worksheet = writer.sheets["Sheet_1"]
        #format = workbook.add_format()
        #format.set_bg_color('#eeeeee')
        #worksheet.set_column(0, 9, 28)

        # the writer has done its job
        writer.close()

        # go back to the beginning of the stream
        output.seek(0)
        #send_file(output, attachment_filename="testing.xlsx", as_attachment=True)
        # finally return the file
        return send_file(output, attachment_filename="测试表格.xlsx", as_attachment=True, mimetype='	application/vnd.ms-excel')
        #return render_template("admin/test_form.html", title='test form', form=form)

    return render_template("admin/test_form.html", title='test form', form=form)
