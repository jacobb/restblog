import json
import sqlite3

from flask import abort, Flask, request, g, render_template

from models import BlogEntry
from errors import NotFound


# configuration
DATABASE = 'data/blogs.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/', methods=["GET"])
def home():
    d = {
        'entries': BlogEntry.get_all(g.db),
    }
    return render_template("entries.html", **d)


@app.route('/entry/<blog_id>', methods=["GET"])
def blog_entry(blog_id):
    try:
        d = {
            "entry": BlogEntry.get(g.db, blog_id)
        }
    except NotFound:
        abort(404)
    return render_template("entry.html", **d)


# API Views
@app.route('/api', methods=["POST", "GET"])
def api_home():
    if request.method == "POST":
        blog_dict = request.get_json()
        blog_entry = BlogEntry(**blog_dict)
        blog_entry.save(g.db)
        return json.dumps(blog_entry.to_dict())
    elif request.method == "GET":
        entries = BlogEntry.get_all(g.db)
        entry_dicts = [e.to_dict() for e in entries]
        return json.dumps(entry_dicts)


@app.route('/api/<blog_id>', methods=["POST", "GET"])
def api_entry(blog_id):
    if request.method == "PUT":
        blog_dict = request.get_json()
        blog_dict['id'] = blog_id
        blog_entry = BlogEntry(**blog_dict)
        blog_entry.save(g.db)
        return json.dumps(blog_entry.to_dict())
    elif request.method == "GET":
        try:
            blog_entry = BlogEntry.get(g.db, blog_id)
        except NotFound:
            abort(404)
        return json.dumps(blog_entry.to_dict())


if __name__ == '__main__':
    app.run()
