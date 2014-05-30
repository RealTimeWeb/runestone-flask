db.courses
    The list of courses within the system

db.auth_user
    The authorized users in the system. Stores users' name, email address, 
    password, and status (registration pending, accepted, blocked). Notice how
    a user can only have a single course.

db.auth_group
    Stores groups or roles for users in a many-to-many structure. By default, each user is in its own group, but a user can be in multiple groups, and each group can contain multiple users. A group is identified by a role and a description.

db.auth_membership
    Links users and groups in a many-to-many structure.

db.auth_permission
    Links groups and permissions. A permission is identified by a name and, optionally, a table and a record. For example, members of a certain group can have "update" permissions on a specific record of a specific table.

db.auth_event
    Logs changes in the other tables and successful access via CRUD to objects controlled by the RBAC.

db.auth_cas
    Is used for Central Authentication Service (CAS). Every web2py application is a CAS provider and can optionally be a CAS consumer.

db.useinfo
[ insert new useinfo ] 

db.code
[ insert new code ] 

db.acerror_log
[ insert new acerror_log ] 

db.user_highlights
[ insert new user_highlights ] 

db.user_state
[ insert new user_state ] 

db.course_instructor
[ insert new course_instructor ] 

db.chapters
[ insert new chapters ] 

db.sub_chapters
[ insert new sub_chapters ] 

db.user_sub_chapter_progress
[ insert new user_sub_chapter_progress ] 

db.modules
[ insert new modules ] 

db.projects
[ insert new projects ] 

db.scheduler_task
[ insert new scheduler_task ] 

db.scheduler_run
[ insert new scheduler_run ] 

db.scheduler_worker
[ insert new scheduler_worker ] 

acbart@vt.edu | Back to top
© Copyright 2013 Brad Miller, David Ranum