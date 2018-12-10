from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FileField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Length
from app.models import User

#deptList=['App','Operations','Guest']
deptList=[('admin','admin'), ('app','app'),('operations','operations'),('guest','guest')]

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    department = SelectField('Department',coerce=str, choices=deptList, default=1)
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    department = SelectField('Department', coerce=str, choices=deptList, default=1)
    submit = SubmitField('Submit')

class DBRegistrationForm(FlaskForm):
    driver = StringField('Driver', validators=[DataRequired()], default="SQL Server")
    host = StringField('Host Name', validators=[DataRequired()])
    db_name = StringField('DB Name', validators=[DataRequired()])
    login = StringField('Login Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remark = StringField('Remark', validators=[DataRequired()])
    submit = SubmitField('Register')

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
