from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import Database
import os


class FxEnhancementForm(FlaskForm):
    _path_1 ="Q:"
    _path_2 = "iBoss2"
    _path_3 = "iBoss2 Tools"
    _path_4 = "FX Enhancement"
    _path_5 = "fx_rate_template.xlsx"
    folder_path = os.path.join(_path_1 + os.sep, _path_2, _path_3, _path_4)
    fx_rate_template_path = os.path.join(_path_1 + os.sep, _path_2, _path_3, _path_4, _path_5)

    database = QuerySelectField(query_factory=lambda: Database.query.all()
                                , default = lambda: Database.query.filter_by(remark="Prod-Query-iBoss2").first()
                                , render_kw={'disabled': True}
                                )
    export_path = StringField('Export Files to the following path', default=folder_path, render_kw={'readonly': True})
    fx_file = FileField('Please import FX file!',
                        validators=[FileAllowed(["xls","xlsx"], 'Excel File only!')],
                        default=fx_rate_template_path)
    submit = SubmitField('Submit')
    open_folder = SubmitField('Please Click Submit to Generate Files', render_kw={'disabled': True})

