# -*- coding: utf-8 -*-
### required - do no delete
import json
from urllib import unquote
import time

def user():
    # this is kinda hacky but it's the only way I can figure out how to pre-populate
    # the course_id field

    if not request.args(0):
        redirect(URL('default', 'user/login'))

    if 'register' in request.args(0):
        # If we can't pre-populate, just set it to blank.
        # This will force the user to choose a valid course name
        db.auth_user.course_id.default = ''

        # Otherwise, use the referer URL to try to pre-populate
        ref = request.env.http_referer
        if ref:
            ref = unquote(ref)
            if '_next' in ref:
                ref = ref.split("_next")
                url_parts = ref[1].split("/")
            else:
                url_parts = ref.split("/")

            for i in range(len(url_parts)):
                if "static" in url_parts[i]:
                    course_name = url_parts[i+1]
                    db.auth_user.course_id.default = course_name
                    break

    form = auth()

    if 'register' in request.args(0) and request.janrain_form:
        # add the Janrain login form
        form[0][5][2] = ''
        form = (DIV(form, request.janrain_form.login_form()))

    if 'profile' in request.args(0):
        form.vars.course_id = auth.user.course_name
        print form
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

            redirect(URL('default', 'index'))

    if 'login' in request.args(0):
        # add info text re: using local auth. CSS styled to match text on Janrain form
        sign_in_text = TR(TD('Sign in with your Runestone Interactive account', _colspan='3'), _id='sign_in_text')
        form[0][0].insert(0, sign_in_text)


    # this looks horrible but it seems to be the only way to add a CSS class to the submit button
    try:
        form.element(_id='submit_record__row')[1][0]['_class']='btn btn-default'
    except AttributeError: # not all auth methods actually have a submit button (e.g. user/not_authorized)
        pass

    return dict(form=form)

def download(): return response.download(request,db)
def call(): return service()
### end requires

#@auth.requires_login()
def index():
    if auth.user:
        course = db(db.courses.id == auth.user.course_id).select(db.courses.course_name).first()
        redirect('/%s/static/%s/index.html' % (request.application,course.course_name))
    else:
        if request.cookies.has_key('ipuser'):
            sid = request.cookies['ipuser'].value
            setCookie = True
        else:
            sid = str(int(time.time()*1000))+"@"+request.client
            setCookie = True
    return dict()
    
    if 'boguscourse' in course.course_name:
        # if login was handled by Janrain, user didn't have a chance to choose the course_id;
        # redirect them to the profile page to choose one
        redirect('/%s/default/user/profile?_next=/%s/default/index' % (request.application, request.application))
    else:
        redirect('/%s/static/%s/index.html' % (request.application,course.course_name))

    cohortId = db(db.auth_user.id == auth.user.id).select(db.auth_user.cohort_id).first()

def error():
    return dict()

def about():
    return dict()

def ack():
    return dict()

    
