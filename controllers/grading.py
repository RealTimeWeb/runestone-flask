# -*- coding: utf-8 -*-
### required - do no delete
import json
from urllib import unquote
import time

def overview():
    s = ""
    subchapters = []
    for row in db().select(db.exercises.ALL, db.chapters.ALL,
                           left=db.chapters.on(db.exercises.chapter==db.chapters.id),
                           orderby=db.chapters.number):
        s += ", ".join(map(str, row)) + "<br>\n"
        subchapters.append(row.exercises.chapter + "/" + row.exercises.subchapter)
    users = []
    for row in db().select(db.auth_user.ALL, orderby=db.auth_user.last_name):
        users.append(row.email+" ({} {})".format(row.first_name, row.last_name))
    return dict(subchapters=subchapters, users=users)

def by_student():
    return dict()
    
def by_exercise():
    return dict()