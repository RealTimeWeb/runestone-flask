#!/usr/bin/env python

import datetime

from flask import Blueprint, render_template
from flask import Flask, redirect, url_for, session, request, jsonify, g

from flask_oauthlib.client import OAuthException

from main import google
from models.models import db, User, get_course_id_from_name
from helpers import login_required

from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, SubmitField

users = Blueprint('users', __name__, url_prefix='/users')

@users.route('/')
def index():
    return render_template('users/index.html', 
                           response= {"title": "TITLTE"},
                           user= g.user)
                       
@users.route('/profile/')
@login_required
def profile():
    g.user.course
        
    """progress = db((db.user_state.user_id == auth.user.id) & 
                  (db.user_state.course_id == auth.user.course_name)).select()
    if progress:
        progress = progress[0]
    else:
        progress = {}
    Field('last_page_url','string'),
    Field('last_page_hash','string'),
    Field('last_page_chapter','string'),
    Field('last_page_subchapter','string'),
    Field('last_page_scroll_location','string'),
    Field('last_page_accessed_on','datetime'),
    if form.process().accepted:
        # auth.user session object doesn't automatically update when the DB gets updated
        auth.user.update(form.vars)
        auth.user.course_name = db(db.auth_user.id == auth.user.id).select()[0].course_name
        chapter_label = db(db.chapters.course_id == auth.user.course_name).select()[0].chapter_label
        if db((db.user_sub_chapter_progress.user_id == auth.user.id) & (db.user_sub_chapter_progress.chapter_id == chapter_label)).count() == 0:
            db.executesql('''
               INSERT INTO user_sub_chapter_progress(user_id, chapter_id,sub_chapter_id, status)
               SELECT %s, chapters.chapter_label, sub_chapters.sub_chapter_label, -1
               FROM chapters, sub_chapters where sub_chapters.chapter_id = chapters.id and chapters.course_id = '%s';
            ''' % (auth.user.id, auth.user.course_name))

        redirect(URL('default', 'index'))"""
    return render_template('users/profile.html',
                           user=g.user,
                           response = {"title": "TITEIT"},
                           progress = {})

@users.route('/login/')
def login():
    return google.authorize(callback=url_for('users.authorized', _external=True))
    
@users.route('/logout/')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('users.index'))

@users.route('/authorized/')
@google.authorized_handler
def authorized(resp):
    if resp is None or isinstance(resp, OAuthException):
        return resp.message + ": " + resp.data.get('error_description', "Unknown error")
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    data = me.data
    user = db.session.query(User).filter(User.email == data['email']).first()
    if user:
        user.first_name = data.get("given_name", user.first_name)
        user.last_name = data.get("family_name", user.last_name)
        user.gender = data.get("gender", user.gender)
        user.picture = data.get("picture", user.picture)
        user.modified_on = default=datetime.datetime.utcnow()
    else:
        user = User(first_name=data.get('given_name', 'NoFirstName'),
                    last_name=data.get('family_name', 'NoLastName'),
                    email=data.get('email', data['id']), #We gotta have something
                    gender = data.get('gender', 'unspecified'),
                    picture = data.get('picture', url_for("static", filename='images/anon.jpg')),
                    course = get_course_id_from_name('compthink'),
                    cohort = 0,
                    active = data.get('email', '').endswith('vt.edu'))
        db.session.add(user)
    session['user_email'] = user.email
    db.session.commit()
    return redirect(url_for('users.profile'))
    
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')
    