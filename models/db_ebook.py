# Files in the model directory are loaded in alphabetical order.  This one needs to be loaded after db.py

"""
useinfo: basically, the event log. Terrible, terrible name.
"""
db.define_table('useinfo',
  Field('timestamp','datetime'),
  Field('sid','string'),
  Field('event','string'),
  Field('act','string'),
  Field('div_id','string'),
  Field('course_id','string'),
  migrate='runestone_useinfo.table'
)

db.define_table('annotations',
    Field('timestamp', 'datetime'),
    Field('student', 'string'),
    Field('chapter', 'string'),
    Field('subchapter', 'string'),
    Field('div_id', 'string'),
    Field('start', 'integer'),
    Field('stop', 'integer'),
    Field('comment', 'string')#,
    #migrate='runestone_annotations.table'
)

db.define_table('code',
  Field('acid','string'),
  Field('code','text'),
  Field('course_id','string'),
  Field('grade','double'),
  Field('sid','string'),
  Field('timestamp','datetime'),
  Field('comment','text'),
  migrate='runestone_code.table'
)

db.define_table('exercises',
    Field('number', 'integer'),
    Field('chapter', 'string'),
    Field('subchapter', 'string'),
    Field('type', 'string'),
    Field('cohort', 'boolean'),
    Field('div_id', 'string'),
    #migrate='runestone_exercises.table'
)

db.define_table('submissions',
    Field('timestamp', 'datetime'),
    Field('student', 'string'),
    Field('chapter', 'string'),
    Field('subchapter', 'string'),
    Field('div_id', 'string'),
    Field('solution', 'text'),
    Field('feedback', 'text'),
    Field('override', 'string'),
    #migrate='runestone_submissions.table'
)

db.define_table('acerror_log',
                Field('timestamp','datetime'),
                Field('sid','string'),
                Field('div_id','string'),
                Field('course_id','string'),
                Field('code','text'),
                Field('emessage','text'),
                migrate='runestone_acerror_log.table'
                )

##table to store highlights saved by the user
db.define_table('user_highlights',
  Field('created_on','datetime'),
  Field('user_id','integer'),
  Field('course_id','string'),
  Field('parent_class','string'), #class of the parent container
  Field('json_range','text'), #range JSON of the highlight
  Field('chapter_url','text'),
  Field('sub_chapter_url','text'),
  Field('method','string'), #self / Imported from friend
  Field('is_active','integer', default=1), #0 - deleted / inactive. 1 - active
  migrate='runestone_user_highlights.table'
)

##table to store the last position of the user. 1 row per user, per course
db.define_table('user_state',
  Field('user_id','integer'),
  Field('course_id','string'),
  Field('last_page_url','string'),
  Field('last_page_hash','string'),
  Field('last_page_chapter','string'),
  Field('last_page_subchapter','string'),
  Field('last_page_scroll_location','string'),
  Field('last_page_accessed_on','datetime'),
  migrate='runestone_user_state.table'
)

# Table to match instructor(s) to their course(s)
db.define_table('course_instructor',
    Field('course', db.courses ),
    Field('instructor', db.auth_user),
    migrate='runestone_course_instructor.table'
)

