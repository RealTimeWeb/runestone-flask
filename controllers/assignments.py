#!/usr/bin/env python

from flask import Blueprint
from flask import Flask, redirect, url_for, session, request, jsonify

from main import google

assignments = Blueprint('assignments', __name__, url_prefix='/assignments')

@assignments.route('/')
def index():
    return 'Assignments'