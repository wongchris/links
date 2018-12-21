from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from app.models import Database
import os
from flask import current_app


class BatchSendEmailForm(FlaskForm):
    bcc = StringField('BCC', default="")
    sender = StringField('Sender Mail', validators=[DataRequired()], default="notice@indsec.com.hk")
    sender_name = StringField('Sender Name', default="興證國際")
    subject = StringField('Sender Subject', default="Test Sub")
    attach = FileField('Attach File')
    pause_per_email = StringField('Pause per email(second)', default="5")
    no_of_batch = StringField('How many email as a batch', default="80")
    hibernate_time = StringField('Hibernate time(second) when meet Batch Maximum', default="2")
    recipient = StringField("Recipient", default="chris.wong@xyzq.com.hk")
    html_body = TextAreaField("HTML Body")
    submit = SubmitField('Send')

class ExportExcelForm(FlaskForm):
    database = QuerySelectField(query_factory=lambda: Database.query.all())
    test_connection = SubmitField('Test DB Connection')
    files_list = os.listdir(os.getcwd() + "/uploads")
    list = [(f, f) for f in files_list if f.rsplit('.', 1)[1] == 'sql']
    files = SelectField('Choose SQL Files', choices=list, id='select_files')
    sql_content = TextAreaField('SQL Content')
    #export_path = StringField('Export Files to the following path')
    submit = SubmitField('Submit')


