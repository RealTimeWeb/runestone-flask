# Built-in imports
import json
import datetime
import logging
import time
from collections import Counter

# Flask imports
from flask import Blueprint
from flask import Flask, redirect, url_for, session, request, jsonify, g, make_response

# Runestone imports
from helpers import crossdomain
from models.models import db, UseInfo, User, CodeErrorLog

ajax = Blueprint('ajax', __name__, url_prefix='/ajax')

def get_user_and_cookie_status():
    """
    Returns the sid and cookie status for the current user, which depends on
    whether the user has been logged in.
    
    Strictly internal. TODO: How do we "hide" internal functions from web2py?
    
    :returns: `str`, `bool`
    """
    if g.user:
        return (g.user.id, False)
    else:
        return ('Guest', True)
    
@ajax.route('/hsb_log/', methods=['GET', 'POST'])
@crossdomain(origin="*")
def hsb_log():
    """
    Human Subjects Board Log
    This is apparently the critical "user did something" recording method.
    """
    sid, set_cookie = get_user_and_cookie_status()
    act = request.values.get('act')
    div_id = request.values.get('div_id')
    event = request.values.get('event')
    course = request.values.get('course')
    # Store activity in database
    db.session.add(UseInfo(student=sid, event=event, act=act, 
                           div_id=div_id, course_id=course))
    db.session.commit()
    # Create Response
    response = jsonify({'log': True})
    if set_cookie:
        response.set_cookie('ipuser', sid, max_age=24*3600*90)
    return response
    
@ajax.route('/run_log/', methods=['GET', 'POST'])
@crossdomain(origin="*")
def run_log():
    """
    Log errors and runs with code
    """
    sid, set_cookie = get_user_and_cookie_status()
    div_id = request.values.get('div_id')
    course = request.values.get('course')
    code = request.values.get('code')
    error_info = request.values.get('errinfo')
    if error_info != 'success':
        event = 'ac_error'
        act = error_info
    else:
        act = 'run'
        event = 'activecode'
    # Store in database
    db.session.add(CodeErrorLog(student=sid,div_id=div_id,course_id=course,
                                code=code,error_message=error_info))
    db.session.add(UseInfo(student=sid, event=event, act=act, 
                           div_id=div_id, course_id=course))
    db.session.commit()
    # Create Response
    response = jsonify({'log': True})
    if set_cookie:
        response.set_cookie('ipuser', sid, max_age=24*3600*90)
    return response

