from app.app_team.forms import BatchSendEmailForm, ExportExcelForm
from app.email import send_email
from flask import current_app, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app.app_team import bp
import pyodbc
import os


@bp.route('/app')
def app_team():
    return render_template("app_team/app_team.html", title='app_team Page')


@bp.route('/batch_send_email', methods=['GET', 'POST'])
@login_required
def batch_send_email():
    if current_user.is_anonymous or current_user.department not in ['admin','app']:
        return redirect(url_for('main.index'))
    form = BatchSendEmailForm()

    recipients = []

    if form.validate_on_submit():
        recipients.append(form.recipient.data)
        send_email(subject=form.sender_name.data + '-' + form.subject.data
                   , sender=form.sender.data
                   , recipients=recipients
                   , text_body="Hello World!"
                   , html_body="<p>Hello World!</p>"
                   , attach=form.attach.data)
        flash('Email Sent to ' + form.recipient.data)
        return redirect(url_for('app_team.batch_send_email'))
    return render_template("app_team/batch_send_email.html", title='Email', form=form)


@bp.route('/export_excel', methods=['GET', 'POST'])
@login_required
def export_excel():
    if current_user.is_anonymous or current_user.department not in ['admin','app']:
        return redirect(url_for('main.index'))
    form = ExportExcelForm()

    #form.sql_content.data = "Hello World"
    if request.method == 'POST':
        try:
            if request.form['file_val']:
                print(request.form['file_val'])
                render_template("app_team/export_excel.html", title='Export Excel', form=form)
        except:
            pass
        if form.validate_on_submit():
            if form.test_connection.data:
                try:
                    database = form.database.data
                    conn = pyodbc.connect('driver={%s};server=%s;database=%s;uid=%s;pwd=%s' % (database.driver, database.host, database.db_name, database.login, database.get_password()), timeout=3)
                    flash(str(database) + " Connected")
                    return redirect(url_for('app_team.export_excel'))
                except:
                    pass
    return render_template("app_team/export_excel.html", title='Export Excel', form=form)
