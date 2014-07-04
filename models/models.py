import datetime

from main import app

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import UserMixin, RoleMixin

db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    # General user properties
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    gender = db.Column(db.String(255))
    picture = db.Column(db.String(255))
    # Courses
    course = db.Column(db.String(255))
    # Cohorts
    cohort = db.Column(db.Integer())
    # Temporal activity
    active = db.Column(db.Boolean())
    created_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    modified_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    

class Course(db.Model):
    """
    A given book may have several Courses associated with it.
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    term_start_date = db.Column(db.DateTime())
    institution = db.Column(db.String(255))

class CohortMaster(db.Model):
    """
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    created_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    invitation_id = db.Column(db.String(255), unique=True)
    average_time = db.Column(db.Integer())
    is_active = db.Column(db.Integer())
 
class CourseInstructors(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    course = db.Column(db.Integer())
    instructor = db.Column(db.Integer())
    
def get_course_id_from_name(name):
    '''
    '''
    try:
        return Course.query.filter_by(name=name).first().id
    except NoResultFound, e:
        return 0
    except MultipleResultsFound, e:
        return 0

def get_course_name_from_id(id):
    '''
    Converts a course's id to to the course's name, returning either
    'Unknown course' or 'Multiple Courses' if it couldn't find the expected.
    '''
    try:
        matching_courses = Course.query.filter_by(id=id).one().name
    except NoResultFound, e:
        return 'Unknown Course'
    except MultipleResultsFound, e:
        return 'Multiple Courses for id #{}?'.format(id)

def verify_instructor_status(course, instructor):
    """
    Make sure that the instructor specified is actually an instructor for the
    given course.
    """
    if type(course) == str:
        course = db.session.query(Course).filter(Course.name == course).one().id
    temp = db.session.query.filter(CourseInstructors.course == course,
                                   CourseInstructors.instructor == instructor)
    return temp.count() > 0
    
