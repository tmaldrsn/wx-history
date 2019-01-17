from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    abort
)
import sqlite3
import datetime

mod = Blueprint('general', __name__)


@mod.route('/')
def home_page():
    return render_template('general/index.html')
