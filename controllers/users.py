#!/usr/bin/env python

from flask import Blueprint, render_template
from flask import Flask, redirect, url_for, session, request, jsonify

from main import google

users = Blueprint('users', __name__, url_prefix='/users')

@users.route('/')
def index():
    return render_template('users/index.html', 
                           response= {"title": "TITLTE"},
                           auth = {"user": "acbart"})
    """if 'google_token' in session:
        me = google.get('userinfo')
        return jsonify({"data": me.data})
    return redirect(url_for('users.login'))"""

@users.route('/login')
def login():
    return google.authorize(callback=url_for('users.authorized', _external=True))
    
@users.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('users.index'))

@users.route('/authorized')
@google.authorized_handler
def authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    try:
        session['google_token'] = (resp['access_token'], '')
        me = google.get('userinfo')
        return jsonify({"data": me.data})
    except TypeError:
        return resp
    
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')
    