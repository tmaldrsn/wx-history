from website.views import (
    general,
    search,
    stations,
)
from flask import (
    Flask,
    url_for,
    render_template,
    request,
    abort,
)

app = Flask(__name__)


@app.errorhandler(400)
def bad_request(error):
    return render_template('400.html', error=error), 400


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


app.register_blueprint(general.mod)
app.register_blueprint(search.mod)
app.register_blueprint(stations.mod)
