#!/usr/bin/env python

from flask import Blueprint
from flask import Flask, redirect, url_for, session, request, jsonify

from main import google

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
def index():
    if 'google_token' in session:
        me = google.get('userinfo')
        return jsonify({"data": me.data})
    return redirect(url_for('frontend.login'))

@frontend.route('/login')
def login():
    return google.authorize(callback=url_for('frontend.authorized', _external=True))

@frontend.route('/authorized')
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
    