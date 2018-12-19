from flask import Blueprint

bp = Blueprint('app_team', __name__)

from app.app_team import routes
