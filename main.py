"""
Local app (using Electron or similar)

Local file-based database of tests
XML-based (extensible with other ideas)
compression?

metadata:
description, title, test id (MD5 hash), requirements link?

contains tests inputs, outputs, initial conditions, post conditions
graphically modify plots of inputs and expected outputs
control which items appear on which plots, zooming, how many plots to look at
expected outputs have built in +/-dy, +dt error bars (semi-transparent same color)
    this dictates pass critera

ability to load prior run data to compare (does not save to test)
    need to "compress" data to simple paths
    highlight exceedences
    ability to "trace" this data e.g. modify expected output to match

view only web client
graphical diff tool
graphical commit?

suggestions:
http://paperjs.org/examples/path-simplification

DO-178B/C tool verification
"""

from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)

from file_database.database import FileDatabase

from testcase import TestCaseContentManager as TestCase
from os import getcwd as pwd
# TODO: Allow user to choose database directories
db = FileDatabase(pwd()+'/file_testdb', obj_class=TestCase, ext='xml')

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

@app.route("/view/<path:basename>")
def view(basename):
    return str(db._load_obj(db._fullpath_from(basename))) + \
            "\n" + '<a href="'+url_for("search")+'">Back to Search</a>'

@app.route("/edit/<path:basename>")
def edit(basename):
    return str(db._load_obj(db._fullpath_from(basename))) + \
            "\n" + '<a href="'+url_for("search")+'">Back to Search</a>'
