# Built-in imports
import json
import datetime
import logging
import time
from collections import Counter

# Flask imports
from flask import Blueprint
from flask import Flask, redirect, url_for, session, request, jsonify, g

# Runestone imports
from helpers import crossdomain

ajax = Blueprint('ajax', __name__, url_prefix='/ajax')

@ajax.route('/get_user/', methods=['GET', 'POST'])
@crossdomain(origin="*")
def get_user():
    """
    Returns the sid and cookie status for the current user, which depends on
    whether the user has been logged in.
    
    Strictly internal. TODO: How do we "hide" internal functions from web2py?
    
    :returns: `str`, `bool`
    """
    if g.user:
        return "['{}', False]".format(g.user.id)
    else:
        return "['Guest', True]"
    
@ajax.route('/hsblog/', methods=['GET', 'POST'])
@crossdomain(origin="*")
def hsblog():    # Human Subjects Board Log
    """
    This seems pretty pointless...
    """
    sid, set_cookie = get_user()
    act = request.values.get('act')
    div_id = request.values.get('div_id')
    event = request.values.get('event')
    course = request.values.get('course')
    ts = datetime.datetime.now()