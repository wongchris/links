from app.operations.forms import FxEnhancementForm
from app.operations.functions.fx_enhancement import FxEnhancement
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
import subprocess
from app.utils.sys_dir import SystemPath
import os
from app.operations import bp


@bp.route('/operations')
def operations():
    return render_template("operations/operations.html", title='Operation Page')

@bp.route('/fx_enhancement', methods=['GET', 'POST'])
@login_required
def fx_enhancement():
    if current_user.is_anonymous or current_user.department not in ['admin','operations']:
        return redirect(url_for('main.index'))
    form = FxEnhancementForm()
    #print(form.fx_file.data)
    if form.validate_on_submit():
        if form.open_folder.data:
            p = subprocess.Popen([os.path.join(SystemPath.TOOL_DIR, "open_folder.bat"), form.export_path.data],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, errors = p.communicate()
            p.wait()
            return redirect(url_for('operations.fx_enhancement'))
        elif form.submit.data:
            if not form.fx_file.data:
                flash(message="No FX Rate File Imported!", category='error')
                return redirect(url_for('operations.fx_enhancement'))
            fx_enhancement = FxEnhancement(database=form.database.data, fx_file=form.fx_file.data, export_path=form.export_path.data)

            fx_enhancement.export_file()
            return redirect(url_for('operations.fx_enhancement'))

    return render_template("operations/fx_enhancement.html", title='FX Enhancement', form=form)

