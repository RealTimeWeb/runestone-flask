import datetime

from main import app

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import UserMixin, RoleMixin
from sqlalchemy import event

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

class UseInfo(db.Model):
    """
    A log of all the actions taken by users. This includes answers submitted
    through a directive!! I suspect that this system should be broken up into
    some other kind of system.
    """
    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime())
    student = db.Column(db.Integer())
    event = db.Column(db.String(255))
    act = db.Column(db.String(255))
    div_id = db.Column(db.String(255))
    # `div_id` is used because `div` is a reserved SQL word
    course_id = db.Column(db.String(255))

class Annotations(db.Model):
    """
    The ranges and associated comments of a annotated body of text, for the
    Annotate directive.
    """
    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime())
    student = db.Column(db.Integer())
    chapter = db.Column(db.String(255))
    subchapter = db.Column(db.String(255))
    div_id = db.Column(db.String(255))
    start = db.Column(db.Integer())
    stop = db.Column(db.Integer())
    comment = db.Column(db.Text())
    
class Annotations(db.Model):
    """
    The ranges and associated comments of a annotated body of text, for the
    Annotate directive.
    """
    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime())
    acid = db.Column(db.String(255))
    code = db.Column(db.Text())
    course_id = db.Column(db.String(255))
    grade = db.Column(db.String(255))
    student = db.Column(db.String(255))
    comment = db.Column(db.Text())

class Exercises(db.Model):
    """
    The ranges and associated comments of a annotated body of text, for the
    Annotate directive.
    """
    id = db.Column(db.Integer(), primary_key=True)
    chapter = db.Column(db.String(255))
    subchapter = db.Column(db.String(255))
    div_id = db.Column(db.String(255))
    type = db.Column(db.String(255))
    cohort = db.Column(db.Boolean())

class Submissions(db.Model):
    """
    The ranges and associated comments of a annotated body of text, for the
    Annotate directive.
    """
    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime())
    student = db.Column(db.String(255))
    chapter = db.Column(db.String(255))
    subchapter = db.Column(db.String(255))
    div_id = db.Column(db.String(255))
    solution = db.Column(db.Text())
    feedback = db.Column(db.Text())
    override = db.Column(db.String(255))

class ActiveCodeErrorLog(db.Model):
    """
    Formally named acerror_log, this is where Active Code errors are recorded.
    """
    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime())
    student = db.Column(db.String(255)) # formally sid
    div_id = db.Column(db.String(255))
    course_id = db.Column(db.String(255))
    code = db.Column(db.Text())
    error_message = db.Column(db.Text())
    
class UserHighlights(db.Model):
    """
    I don't think this is actually implemented yet, but it appears as if there
    are plans to add book highlighting.
    """
    id = db.Column(db.Integer(), primary_key=True)
    created_on = db.Column(db.DateTime())
    user_id = db.Column(db.Integer())
    course_id = db.Column(db.String(255))
    parent_class = db.Column(db.String(255)) #class of the parent container
    json_range = db.Column(db.Text()) #range JSON of the highlight
    chapter_url = db.Column(db.Text())
    sub_chapter_url = db.Column(db.Text())
    method = db.Column(db.String(255)) #self / Imported from friend
    is_active = db.Column(db.Integer(), default=1) # 0 - deleted / inactive. 1 - active

class UserState(db.Model):
    """
    Stores the last recorded state of the user, e.g., what page they were on
    and where they were.
    Store the last position of the user. 1 row per user, per course.
    """
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    course_id = db.Column(db.String(255))
    last_page_url = db.Column(db.String(255))
    last_page_hash = db.Column(db.String(255))
    last_page_chapter = db.Column(db.String(255))
    last_page_subchapter = db.Column(db.String(255))
    last_page_scroll_location = db.Column(db.String(255))
    last_page_accessed_on = db.Column(db.DateTime())

class Chapters(db.Model):
    """
    Table of all book chapters.
    """
    __tablename__ = 'chapters'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    label = db.Column(db.String(255))
    number = db.Column(db.Integer())
    course_id = db.Column(db.String(255)) # references courses(course_name)

class Subchapters(db.Model):
    """
    Table of all book chapters.
    
    Subchapters is ONE word, no space or anything.
    """
    __tablename__ = 'subchapters'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    label = db.Column(db.String(255))
    number = db.Column(db.Integer())
    chapter_id = db.Column(db.String(255), db.ForeignKey('chapters.id'))
    chapter = db.relationship("Chapter", backref=db.backref('subchapters', order_by=id))
    # Average Time it takes people to complete this subchapter, maybe calculated
    # using a weekly batchjob
    length = db.Column(db.Integer())

class UserChapterProgress(db.Model):
    __tablename__ = 'user_chapter_progress'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('User.id'))
    user = db.relationship("User", backref=db.backref('chapterProgresses', order_by=id))
    chapter_id = db.Column(db.String(255))
    start_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    end_date = db.Column(db.DateTime())
    status = db.Column(db.Integer()) #-1  - not started. 0 - active. 1 - completed
    
class UserSubchapterProgress(db.Model):
    __tablename__ = 'user_subchapter_progress'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('User.id'))
    user = db.relationship("User", backref=db.backref('subchapterProgresses', order_by=id))
    chapter_id = db.Column(db.String(255))
    subchapter_id = db.Column(db.String(255))
    start_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    end_date = db.Column(db.DateTime())
    status = db.Column(db.Integer()) #-1  - not started. 0 - active. 1 - completed

# When a new user is registered we need to add a bunch of rows to the
# user_sub_chapter_progress table.  One for each section/subsection
# This is like a trigger, but will work across all databases.
#
@db.event.listens_for(User, 'after_insert')
def make_progress_entries(mapper, connection, target):
    course_name = get_course_name_from_id(target.course)
    db.session.execute('''
       INSERT INTO user_chapter_progress(user_id, chapter_id, status)
           SELECT {}, chapters.label, -1
           FROM chapters WHERE chapters.course_id = '{}';
        '''.format(target.id, course_name))
    db.session.execute('''
       INSERT INTO user_subchapter_progress(user_id, chapter_id, subchapter_id, status)
           SELECT {}, chapters.label, subchapters.sub_chapter_label, -1
           FROM chapters, subchapters WHERE subchapters.chapter_id = chapters.id and chapters.course_id = '{}';
        '''.format(target.id, course_name))
