from main import user_datastore
from models import db, Course, Cohort

import datetime

def create_courses():
    Course.query.delete()
    ct = Course(name='compthink', 
                term_start_date=datetime.date(2014, 7, 3),
                institution='Virginia Tech',
                default=True)
    db.session.add(ct)
    db.session.commit()
    
def create_cohort():
    Cohort.query.delete()
    default_group = Cohort(name='Default Group',
                           is_active=1,
                           default=True)
    db.session.add(default_group)
    db.session.commit()

def create_roles():
    for role in ('admin', 'editor', 'author'):
        user_datastore.create_role(name=role, description=role)
    db.session.commit()
        
def create_users():
    for u in  (('acbart','acbart@vt.edu','password',['admin'],True),
               ('joe','joe@lp.com','password',['editor'],True),
               ('jill','jill@lp.com','password',['author'],True),
               ('tiya','tiya@lp.com','password',[],False)):
        user_datastore.create_user(username=u[0], email=u[1], password=u[2],
                                   roles=u[3], active=u[4])
        db.session.commit()

def populate_data():
    create_courses()
    create_cohort()