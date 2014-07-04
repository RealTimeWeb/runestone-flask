#!/usr/bin/env python

from flask import Blueprint
from flask import Flask, redirect, url_for, session, request, jsonify

instructor = Blueprint('instructor', __name__)

@instructor.route('/')
def index():
    return render_template('instructor/index.html', 
                           response= {"title": "TITLTE"},
                           user= g.user)