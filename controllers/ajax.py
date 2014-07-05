# Built-in imports
import json
import datetime
import logging
import time
from collections import Counter

# Flask imports
from flask import Blueprint
from flask import Flask, redirect, url_for, session, request, jsonify, g,\
                  make_response, Response

# Runestone imports
from helpers import crossdomain, instructor_required
from models.models import db, UseInfo, User, CodeErrorLog, Code

from main import app

ajax = Blueprint('ajax', __name__, url_prefix='/ajax')

def jsonify_list(content):
    return Response(json.dumps(content),  mimetype='application/json')

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
    
@ajax.route('/hsb_log', methods=['GET', 'POST'])
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
    
@ajax.route('/run_log', methods=['GET', 'POST'])
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

@ajax.route('/save_program', methods=['GET', 'POST'])
@crossdomain(origin="*")
def save_program():
    """
    Ajax Handlers for saving and restoring active code blocks
    """
    acid = request.values.get('acid')
    code = request.values.get('code')
    # Attempt to store in the database
    try:
        db.session.add(Code(student=g.user, acid=acid, code=code,
                            course=g.user.course))
        db.session.commit()
    except Exception as e:
        if g.user:
            return jsonify_list(["ERROR: " + str(e) + "Please copy this error and use the Report a Problem link"])
        else:
            return jsonify_list(["ERROR: You are not logged in.  Copy your code to the clipboard and reload or logout/login"])
    return jsonify_list([acid])
    
@ajax.route('/load_program', methods=['GET', 'POST'])
@crossdomain(origin="*")
def load_program():
    """
    return the program code for a particular acid
    :Parameters:
        - `acid`: id of the active code block
        - `user`: optional identifier for the owner of the code
    :Return:
        - json object containing the source text
    """
    acid = request.values.get('acid')
    sid = request.values.get('sid')
    # Build up query, unless no user then exit with empty response
    if sid:
        query = Code.query.filter_by(student_id=sid, acid=acid)
    elif g.user:
        query = Code.query.filter_by(student=g.user, acid=acid)
    else:
        return jsonify_list([{}])
    # Execute query
    response = {'acid': acid}
    if query.count():
        response['source'] = query.order_by(Code.timestamp).first().code
        if sid:
            response['sid'] = sid
    else:
        app.logger.debug("Did not find anything to load for {}".format(sid))
    return jsonify_list([response])


@ajax.route('/save_grade', methods=['GET', 'POST'])
@crossdomain(origin="*")
@instructor_required
def save_grade():
    id = request.values.get('id')
    grade = request.values.get('grade')
    comment = request.values.get('comment')
    code = Code.query.filter_by(id=id).first()
    if grade:
        code.grade = grade
    else:
        code.comment = comment
    db.session.commit()

@ajax.route('/get_user', methods=['GET', 'POST'])
@crossdomain(origin="*")
def get_user():
    if g.user:
        response = {'email': g.user.email,
                    'nick': g.user.name(),
                    'cohortId': g.user.cohort_id}
    else:        
        response = {'redirect': url_for('users.login')} #?_next=....
    app.logger.debug("Returning login info: {}".format(response))
    return jsonify_list([response])

@ajax.route('/count_users_online', methods=['GET', 'POST'])
@crossdomain(origin="*")
def count_users_online():
    five_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=15)
    count = UseInfo.query.distinct(UseInfo.student).\
                          filter(UseInfo.timestamp >= five_minutes_ago).\
                          count()
    return jsonify_list([{'online':count}])
