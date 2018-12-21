from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.models import User

deptList=[('admin','admin'), ('app','app'),('operations','operations'),('guest','guest')]

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

class TestForm(FlaskForm):
    fx_file = FileField('Please import FX file!',
                        validators=[FileAllowed(["xls", "xlsx"], 'Excel File only!')])
    submit = SubmitField('Submit')

class UploadForm(FlaskForm):
    uploads = FileField('Please choose files to upload!')
    submit = SubmitField(u'Upload')