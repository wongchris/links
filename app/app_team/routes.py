from app.app_team.forms import BatchSendEmailForm
from app.email import send_email
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.app_team import bp

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
