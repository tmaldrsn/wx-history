from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    abort,
    jsonify
)
import sqlite3
import datetime

mod = Blueprint('general', __name__)


@mod.route('/')
def home_page():
    return render_template('general/index.html')


@mod.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a+b)


@mod.route('/add')
def index():
    return render_template('index.html')
