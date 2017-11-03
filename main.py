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
    return render_template("search.html", obj_listing=db.get_objs()) 
    
@app.route("/add", methods=["GET", "POST"])
def add():
    error = None
    if request.method == 'POST':
        error = db.add_obj(request.form["basename"])
        if not error:
            return redirect(url_for("edit", basename=fname))
    return render_template("add.html", error=error)

@app.route("/view/<path:basename>")
def view(basename):
    obj = [o for o in db.get_objs(basename)][0]
    print(obj)
    return render_template("view.html", obj=obj)

@app.route("/edit/<path:basename>", methods=["GET", "POST"])
def edit(basename):
    error = None
    obj = [o for o in db.get_objs(basename)][0]
    if request.method == 'POST':
        if request.form["function"] == "Update Title":
            error = db.apply(lambda o: o.set_title(request.form["Title"]), objs=[obj])
        if not error:
            return redirect(url_for("view", basename=basename))
    return render_template("edit.html", error=error, obj=obj)
