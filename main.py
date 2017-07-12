from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)

from file_database.database import FileDatabase

from testcase import TestCaseContentManager as TestCase
from os import getcwd as pwd
# TODO: Allow user to choose database directories
db = FileDatabase(pwd()+'/file_testdb', obj_class=TestCase)

@app.route("/")
@app.route("/search")
def search():
    return "\n".join(['<a href="'+url_for("view", basename=o.basename)+\
            '">'+o.get_title()+'</a>' for o in db.get_objs()]) + \
            "\n" + '<a href="'+url_for("add")+'">Add Another</a>'
    
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == 'POST':
        fname = request.form["basename"]
        db.add_obj(fname)
        return redirect(url_for("edit", basename=fname))
    return '''
    <form method="post">
        <input name="basename">
        <input type="submit" value="Add Test">
    </form>
    '''

@app.route("/view/<basename>")
def view(basename):
    return str(db._load_obj(db._fullpath_from(basename))) + \
            "\n" + '<a href="'+url_for("search")+'">Back to Search</a>'

@app.route("/edit/<basename>")
def edit(basename):
    return str(db._load_obj(db._fullpath_from(basename))) + \
            "\n" + '<a href="'+url_for("search")+'">Back to Search</a>'
