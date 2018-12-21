from app import db, uploads
from app.models import User, Database
from app.admin.forms import DBRegistrationForm, RegistrationForm, TestForm, UploadForm
from flask import render_template, flash, redirect, url_for, request,send_file, Response
from flask_login import current_user, login_required
import pyodbc
import json
import pandas as pd
from io import BytesIO
from app.admin import bp
import os
from flask import current_app, send_from_directory
import time
import hashlib
from app.admin.functions.uploadfile import Uploadfile
import simplejson
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

@bp.route('/admin')
def admin():
    if current_user.is_anonymous:
        return redirect(url_for('main.index'))
    return render_template("admin/admin.html", title='admin Page')

# region db management
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
# endregion

# region ser management
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
# endregion

# region file_uploader
@bp.route('/file_uploader', methods=['GET', 'POST'])
@login_required
def file_uploader():
    if current_user.is_anonymous or current_user.department not in ['admin']:
        return redirect(url_for('main.index'))
    form = TestForm()
    #print(form.fx_file.data)
    if form.validate_on_submit():
        pass
    return render_template("admin/file_uploader.html", title='File Uploader', form=form)

@bp.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        #files = request.files['file']
        files = request.files.getlist('file')
        if files:
            for file in files:
                abs_file_path = uploads.path(secure_filename(file.filename))
                if not os.path.exists(abs_file_path):
                    uploads.save(file)
                    size = os.path.getsize(abs_file_path)
                    result = Uploadfile(name=secure_filename(file.filename), type=file.content_type, size=size)
                else:
                    result = Uploadfile(name=secure_filename(file.filename), type=file.content_type, size=0, not_allowed_msg="File already exists!")
        return simplejson.dumps({"files": [result.get_file()]})
    if request.method == 'GET':
        files = [f for f in os.listdir(current_app.config['UPLOADED_UPLOADS_DEST']) if
                 os.path.isfile(os.path.join(current_app.config['UPLOADED_UPLOADS_DEST'], f))]
        file_display = []
        for f in files:
            size = os.path.getsize(os.path.join(current_app.config['UPLOADED_UPLOADS_DEST'], f))
            file_saved = Uploadfile(name=f, size=size)
            file_display.append(file_saved.get_file())
        return simplejson.dumps({"files": file_display})
    return render_template("admin/file_uploader.html", title='File Uploader')

@bp.route("/uploads/<string:filename>", methods=['GET'])
def get_file(filename):
    return send_from_directory(os.path.join(current_app.config['UPLOADED_UPLOADS_DEST']), filename=filename)

@bp.route("/delete/<string:filename>", methods=['DELETE'])
def delete(filename):
    file_path = os.path.join(current_app.config['UPLOADED_UPLOADS_DEST'], filename)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return simplejson.dumps({filename: 'True'})
        except:
            return simplejson.dumps({filename: 'False'})

# endregion

# region upload_files
@bp.route('/upload_files', methods=['GET', 'POST'])
@login_required
def upload_files():
    if current_user.is_anonymous or current_user.department not in ['admin']:
        return redirect(url_for('main.index'))
    form = UploadForm()
    if form.validate_on_submit():
        for filename in request.files.getlist('uploads'):
            print(filename)
            uploads.save(filename)
        success = True
    else:
        success = False
    return render_template('admin/upload_files.html', form=form, success=success)

@bp.route('/manage_files', methods=['GET', 'POST'])
@login_required
def manage_files():
    if current_user.is_anonymous or current_user.department not in ['admin']:
        return redirect(url_for('main.index'))
    files_list = os.listdir(current_app.config['UPLOADED_UPLOADS_DEST'])
    return render_template('admin/manage_files.html', files_list=files_list)


@bp.route('/open/<filename>')
@login_required
def open_file(filename):
    if current_user.is_anonymous or current_user.department not in ['admin']:
        return redirect(url_for('main.index'))
    file_url = uploads.url(filename)
    return render_template('admin/browser_file.html', file_url=file_url)


@bp.route('/delete/<filename>')
@login_required
def delete_file(filename):
    if current_user.is_anonymous or current_user.department not in ['admin']:
        return redirect(url_for('main.index'))
    #uploads.path -- absolute path
    file_path = uploads.path(filename)
    os.remove(file_path)
    return redirect(url_for('admin.manage_files'))

# endregion