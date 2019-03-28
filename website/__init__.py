from website.views import (
    general,
    search,
    stations,
)
from website import observations as gobs
from flask import (
    Flask,
    url_for,
    render_template,
    request,
    abort,
    redirect
)


import numpy as np
import pandas as pd
import os


server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')
server.config.from_object('websiteconfig')


@server.errorhandler(400)
def bad_request(error):
    return render_template('400.html', error=error), 400


@server.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


server.register_blueprint(general.mod)
server.register_blueprint(search.mod)
server.register_blueprint(stations.mod)
