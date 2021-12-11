from flask import render_template, redirect, url_for
from . import homeBP

@homeBP.route("/")
@homeBP.route("/index.html")
def home():
    return render_template("index.html")
