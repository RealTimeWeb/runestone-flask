import datetime

from main import app

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
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
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    gender = db.Column(db.String(255))
    picture = db.Column(db.String(255))
    # Courses
    course_id = db.Column(db.Integer(), db.ForeignKey('course.id'))
    course = db.relationship("Course", backref=db.backref('students', order_by=id))
    # Cohorts
    cohort_id = db.Column(db.Integer(), db.ForeignKey('cohort.id'))
    cohort = db.relationship("Cohort", backref=db.backref('students', order_by=id))
    # Temporal activity
    active = db.Column(db.Boolean())
    created_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    modified_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    
    def __repr__(self):
        return '<{} {}>'.format('Instructor' if self.is_instructor()
                                             else 'Student',
                                self.email)
    def is_instructor(self, course=None):
        if course is None:
            return CourseInstructors.query.filter_by(instructor_id= self.id).count() > 0
        if type(course) == str:
            course = db.session.query(Course).filter(Course.name == course).one().id
        temp = db.session.query.filter(CourseInstructors.course == course,
                                       CourseInstructors.instructor_id == self.id)
        return temp.count() > 0 

class Course(db.Model):
    """
    A given book may have several Courses associated with it.
    """
    __tablename__ = 'course'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    term_start_date = db.Column(db.DateTime())
    institution = db.Column(db.String(255))
    default = db.Column(db.Boolean(), default=False)
    
def get_default_course():
    """
    Returns the first course with default=True
    """
    return Course.query.filter_by(default=True).first()

class Cohort(db.Model):
    """
    """
    __tablename__ = 'cohort'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    created_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    invitation_id = db.Column(db.String(255), unique=True)
    average_time = db.Column(db.Integer())
    is_active = db.Column(db.Integer())
    default = db.Column(db.Boolean(), default=False)
    
def get_default_cohort():
    """
    Returns the first cohort with 
    """
    return Cohort.query.filter_by(default=True).first()
 
class CourseInstructors(db.Model):
    __tablename__ = 'course_instructors'
    id = db.Column(db.Integer(), primary_key=True)
    course_id = db.Column(db.Integer(), db.ForeignKey('course.id'))
    course = db.relationship("Course", backref=db.backref('instructors', order_by=id))
    instructor_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    instructor = db.relationship("User")
    
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
    __tablename__ = 'use_info'
    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    student = db.Column(db.Integer())
    event = db.Column(db.String(255))
    act = db.Column(db.String(255))
    div_id = db.Column(db.String(255))
    # `div_id` is used because `div` is a reserved SQL word
    course_id = db.Column(db.String(255))
    def __repr__(self):
        return '<Use Info {} ({})>'.format(id, event)

class Annotations(db.Model):
    """
    The ranges and associated comments of a annotated body of text, for the
    Annotate directive.
    """
    __tablename__ = 'annotations'
    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime())
    student = db.Column(db.Integer())
    chapter = db.Column(db.String(255))
    subchapter = db.Column(db.String(255))
    div_id = db.Column(db.String(255))
    start = db.Column(db.Integer())
    stop = db.Column(db.Integer())
    comment = db.Column(db.Text())

class Exercises(db.Model):
    """
    The ranges and associated comments of a annotated body of text, for the
    Annotate directive.
    """
    __tablename__ = 'exercises'
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
    __tablename__ = 'submissions'
    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime())
    student = db.Column(db.String(255))
    chapter = db.Column(db.String(255))
    subchapter = db.Column(db.String(255))
    div_id = db.Column(db.String(255))
    solution = db.Column(db.Text())
    feedback = db.Column(db.Text())
    override = db.Column(db.String(255))

class CodeErrorLog(db.Model):
    """
    Formally named acerror_log, this is where Active Code errors are recorded.
    """
    __tablename__ = 'code_error_log'
    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    student = db.Column(db.String(255)) # formally sid
    div_id = db.Column(db.String(255))
    course_id = db.Column(db.String(255))
    code = db.Column(db.Text())
    error_message = db.Column(db.Text())
    def __repr__(self):
        return '<Code Error Log {}>'.format(id)
    
class UserHighlights(db.Model):
    """
    I don't think this is actually implemented yet, but it appears as if there
    are plans to add book highlighting.
    """
    __tablename__ = 'user_highlights'
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
    __tablename__ = 'user_state'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    course_id = db.Column(db.String(255))
    last_page_url = db.Column(db.String(255))
    last_page_hash = db.Column(db.String(255))
    last_page_chapter = db.Column(db.String(255))
    last_page_subchapter = db.Column(db.String(255))
    last_page_scroll_location = db.Column(db.String(255))
    last_page_accessed_on = db.Column(db.DateTime())

class Chapter(db.Model):
    """
    Table of all book chapters.
    """
    __tablename__ = 'chapter'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    label = db.Column(db.String(255))
    number = db.Column(db.Integer())
    course_id = db.Column(db.String(255)) # references courses(course_name)

class Subchapter(db.Model):
    """
    Table of all book subchapters.
    
    Subchapters is ONE word, no space or anything.
    """
    __tablename__ = 'subchapter'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    label = db.Column(db.String(255))
    number = db.Column(db.Integer())
    chapter_id = db.Column(db.String(255), db.ForeignKey('chapter.id'))
    chapter = db.relationship("Chapter", backref=db.backref('subchapter', order_by=id))
    # Average Time it takes people to complete this subchapter, maybe calculated
    # using a weekly batchjob
    length = db.Column(db.Integer())

class UserChapterProgress(db.Model):
    __tablename__ = 'user_chapter_progress'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship("User", backref=db.backref('chapterProgresses', order_by=id))
    chapter_id = db.Column(db.Integer(), db.ForeignKey('chapter.id'))
    start_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    end_date = db.Column(db.DateTime())
    status = db.Column(db.Integer()) #-1  - not started. 0 - active. 1 - completed
    
class UserSubchapterProgress(db.Model):
    __tablename__ = 'user_subchapter_progress'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship("User", backref=db.backref('subchapterProgresses', order_by=id))
    chapter_id = db.Column(db.Integer(), db.ForeignKey('chapter.id'))
    subchapter_id = db.Column(db.Integer(), db.ForeignKey('subchapter.id'))
    start_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    end_date = db.Column(db.DateTime())
    status = db.Column(db.Integer()) #-1  - not started. 0 - active. 1 - completed

# When a new user is registered we need to add a bunch of rows to the
# user_sub_chapter_progress table.  One for each section/subsection
# This is like a trigger, but will work across all databases.
#
@db.event.listens_for(User, 'after_insert')
def make_progress_entries(mapper, connection, target):
    db.session.execute('''
       INSERT INTO user_chapter_progress(user_id, chapter_id, status)
           SELECT {}, chapter.label, -1
           FROM chapter WHERE chapter.course_id = '{}';
        '''.format(target.id, target.course_id))
    db.session.execute('''
       INSERT INTO user_subchapter_progress(user_id, chapter_id, subchapter_id, status)
           SELECT {}, chapter.label, subchapter.label, -1
           FROM chapter, subchapter WHERE subchapter.chapter_id = chapter.id and chapter.course_id = '{}';
        '''.format(target.id, target.course_id))

class CohortPlan(db.Model):
    __tablename__ = 'cohort_plan'
    id = db.Column(db.Integer(), primary_key=True)
    cohort_id = db.Column(db.Integer(), db.ForeignKey('cohort.id'))
    cohort = db.relationship("Cohort", backref=db.backref('plans', order_by=id))
    chapter_id = db.Column(db.Integer(), db.ForeignKey('chapter.id'))
    chapter = db.relationship("Chapter", backref=db.backref('cohort_plans', order_by=id))
    start_date = db.Column(db.DateTime())
    end_date = db.Column(db.DateTime())
    actual_end_date = db.Column(db.DateTime()) #actual date when everyone completed the chapter
    note = db.Column(db.String(255))
    status = db.Column(db.String(255))
    created_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    created_by = db.Column(db.Integer(), db.ForeignKey('user.id'))
    is_active = db.Column(db.Integer(), default=1) #0 - deleted / inactive. 1 - active

class CohortPlanRevisions(db.Model):
    __tablename__ = 'cohort_plan_revisions'
    id = db.Column(db.Integer(), primary_key=True)
    plan_id = db.Column(db.Integer(), db.ForeignKey('cohort_plan.id'))
    plan = db.relationship("CohortPlan", backref=db.backref('revisions', order_by=id))
    revision_no = db.Column(db.Integer()) #Revision no of the modified plan. Calculated by max(revision_no) + 1 where cohort_id and chapter_id are matched.
    cohort_id = db.Column(db.Integer(), db.ForeignKey('cohort.id'))
    cohort = db.relationship("Cohort", backref=db.backref('revisions', order_by=id))
    chapter_id = db.Column(db.Integer(), db.ForeignKey('chapter.id'))
    chapter = db.relationship("Chapter", backref=db.backref('revisions', order_by=id))
    start_date = db.Column(db.DateTime())
    end_date = db.Column(db.DateTime())
    actual_end_date = db.Column(db.DateTime()) #actual date when everyone completed the chapter
    note = db.Column(db.String(255))
    status = db.Column(db.String(255))
    created_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    created_by = db.Column(db.Integer(), db.ForeignKey('user.id'))
    is_active = db.Column(db.Integer(), default=1) #0 - deleted / inactive. 1 - active
    
class CohortPlanResponses(db.Model):
    __tablename__ = 'cohort_plan_responses'
    id = db.Column(db.Integer(), primary_key=True)
    plan_id = db.Column(db.Integer()) #combination of plan and revision define which iteration was this response for
    response = db.Column(db.Integer()) #-1 - awaiting response. 0 - rejected. 1 - accepted
    response_by = db.Column(db.Integer(), db.ForeignKey('user.id'))
    response_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

class UserComments(db.Model):
    __tablename__ = 'user_comments'
    id = db.Column(db.Integer(), primary_key=True)
    cohort_id = db.Column(db.Integer(), db.ForeignKey('cohort.id'))
    cohort = db.relationship("Cohort", backref=db.backref('comments', order_by=id))
    chapter_id = db.Column(db.Integer(), db.ForeignKey('chapter.id'))
    chapter = db.relationship("Chapter", backref=db.backref('comments', order_by=id))
    comment = db.Column(db.Text())
    comment_by_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    comment_by = db.relationship("User", backref=db.backref('comments', order_by=id))
    comment_parent_id = db.Column(db.Integer(), db.ForeignKey('user_comments.id'))
    comment_parent = db.relationship("UserComments", remote_side=[id])
    comment_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    
class Section(db.Model):
    # General user properties
    __tablename__ = 'section'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    course_id = db.Column(db.Integer(), db.ForeignKey('course.id'))
    course = db.relationship("Course", backref=db.backref('sections', order_by=id))
    
SectionUsers = db.Table('section_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('section_id', db.Integer(), db.ForeignKey('section.id')))
        
class CodeExerciseDeadline(db.Model):
    # was 'pipactex_deadline'
    __tablename__ = 'code_exercise_deadline'
    id = db.Column(db.Integer(), primary_key=True)
    acid_prefix = db.Column(db.String(255))
    deadline = db.Column(db.DateTime())
    section_id = db.Column(db.Integer(), db.ForeignKey('section.id'))
    section = db.relationship("Section", backref=db.backref('code_exercise_deadlines', order_by=id))

class Modules(db.Model):
    __tablename__ = 'modules'
    id = db.Column(db.Integer(), primary_key=True)
    shortname = db.Column(db.String(255))
    description = db.Column(db.Text())
    pathtofile = db.Column(db.String(255))

class Projects(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer(), primary_key=True)
    project_code = db.Column(db.String(255))
    description = db.Column(db.String(255))
    
import grouped_assignments