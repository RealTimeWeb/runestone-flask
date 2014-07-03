from os import path
import os
import shutil
import sys
from sphinx.application import Sphinx

import logging
logger = logging.getLogger("web2py.app.runestone")
logger.setLevel(logging.DEBUG)

# this is for admin links
#   index
#   listassignments
#   listassessments
#   assessdetail
#   gradeassignment
#   showlog
#   studentactivity
#   startdate
#   rebuildcourse
#   buildmodulelist
# use auth.requires_membership('manager')
#
# create a simple index to provide a page of links
# - re build the book
# - list assignments
# - find assignments for a student
# - show totals for all students

# select acid, sid from code as T where timestamp = (select max(timestamp) from code where sid=T.sid and acid=T.acid);


#@auth.requires_login()
@auth.requires(lambda: verifyInstructorStatus(auth.user.course_name, auth.user), requires_login=True)
def index():
    row = db(db.courses.id == auth.user.course_id).select(db.courses.course_name).first()
    # get current build info
    # read build info from application/custom_courses/course/build_info
    try:
        mbf = open(path.join('applications',request.application,'build_info'),'r')
        master_build = mbf.read()[:-1]
        mbf.close()
    except:
        master_build = ""

    try:
        mbf = open(path.join('applications',request.application,'custom_courses',row.course_name,'build_info'),'r')
        my_build = mbf.read()[:-1]
        mbf.close()
    except:
        my_build = ""

    my_vers = 0
    mst_vers = 0
    if master_build and my_build:
        mst_vers,mst_bld,mst_hsh = master_build.split('-')
        my_vers,my_bld,my_hsh = my_build.split('-')
        if my_vers != mst_vers:
            response.flash = "Updates available, consider rebuilding"

    return dict(build_info=my_build, master_build=master_build, my_vers=my_vers, mst_vers=mst_vers )

@auth.requires(lambda: verifyInstructorStatus(auth.user.course_name, auth.user), requires_login=True)
def listassignments():
    sid = request.vars.student
    course = db(db.courses.id == auth.user.course_id).select().first()
    if sid:
        q = db((db.code.sid == sid)
             & (db.code.course_id == course.course_name)
             & (db.code.timestamp >= course.term_start_date))
    else:
        q = db((db.code.course_id == auth.user.course_id)
             & (db.code.timestamp >= course.term_start_date))
    prefixes = {}
    for row in q.select(db.code.acid,orderby=db.code.acid,distinct=True):
        acid = row.acid
        acid_prefix = acid.split('_')[0]
        if acid_prefix not in prefixes.keys():
            prefixes[acid_prefix] = []
        prefixes[acid_prefix].append(acid)
    return dict(sections=prefixes,course_id=course.course_name)

@auth.requires(lambda: verifyInstructorStatus(auth.user.course_name, auth.user), requires_login=True)
def listassessments():
    
    course = db(db.courses.id == auth.user.course_id).select().first()
    
    logging.error(course.course_name)
    logging.error(course.term_start_date)
    
    query = '''SELECT *, 
                      (SELECT count(*) 
                           FROM useinfo 
                           WHERE div_id = oui.div_id 
                           AND course_id = '%(course_name)s'),
                      (SELECT count(*) * 1.0 
                           FROM useinfo 
                           WHERE div_id = oui.div_id 
                           AND course_id='%(course_name)s' 
                           AND instr(act, 'correct') > 0)
                       / 
                       (SELECT count(*) 
                           FROM useinfo 
                           WHERE div_id = oui.div_id 
                           AND course_id = '%(course_name)s' ) 
                       AS pct
                   FROM useinfo AS oui
                   WHERE event = 'mChoice'
                   AND DATE(timestamp) >= DATE('%(start_date)s')
                   GROUP BY div_id
                   ORDER BY pct''' % dict(course_name=course.course_name, start_date=course.term_start_date)
    logging.error(db.executesql(query))
    

    query = '''SELECT div_id, 
                      (SELECT count(*) 
                           FROM useinfo 
                           WHERE div_id = oui.div_id 
                           AND course_id = '%(course_name)s'),
                      (SELECT count(*) * 1.0 
                           FROM useinfo 
                           WHERE div_id = oui.div_id 
                           AND course_id='%(course_name)s' 
                           AND instr(act, 'correct') > 0)
                       / 
                       (SELECT count(*) 
                           FROM useinfo 
                           WHERE div_id = oui.div_id 
                           AND course_id = '%(course_name)s' ) 
                       AS pct
                   FROM useinfo AS oui
                   WHERE event = 'mChoice'
                   AND DATE(timestamp) >= DATE('%(start_date)s')
                   AND course_id = '%(course_name)s'
                   GROUP BY div_id
                   ORDER BY pct''' % dict(course_name=course.course_name, start_date=course.term_start_date)
    rset = db.executesql(query)
    return dict(solutions=rset)

@auth.requires(lambda: verifyInstructorStatus(auth.user.course_name, auth.user), requires_login=True)
def assessdetail():
    course = db(db.courses.id == auth.user.course_id).select(db.courses.course_name).first()
    q = db( (db.useinfo.div_id == request.vars.id) & (db.useinfo.course_id == course.course_name) )
    res = q.select(db.useinfo.sid,db.useinfo.act,orderby=db.useinfo.sid)
    
    currentSid = res[0].sid
    currentAnswers = []
    answerDict = {}
    totalAnswers = 0
    resultList = []
    correct = ''
    for row in res:
        answer = row.act.split(':')[1]
        answerDict[answer] = answerDict.get(answer,0) + 1
        totalAnswers += 1
        
        if row.sid == currentSid:
            currentAnswers.append(answer)
            if row.act.split(':')[2] == 'correct':
                correct = answer
        else:
            currentAnswers.sort()
            resultList.append((currentSid,currentAnswers))
            currentAnswers = [row.act.split(':')[1]]
            
            currentSid = row.sid

    
    
    currentAnswers.sort()
    resultList.append((currentSid,currentAnswers))
    
    return dict(reslist=resultList, answerDict=answerDict, correct=correct)



@auth.requires(lambda: verifyInstructorStatus(auth.user.course_name, auth.user), requires_login=True)
def gradeassignment():
    sid = request.vars.student
    acid = request.vars.id
    course = db(db.courses.id == auth.user.course_id).select(db.courses.course_name).first()

    section_form=FORM(
        INPUT(_type="hidden", _name="id", _value=acid),
        _class="form-inline",
        _method="GET",
        )
    section_form.append(LABEL(
            INPUT(_name="section_id", _type="radio", _value=""),
            "All Students",
            _class="radio-inline",
            ))
    for section in db(db.sections.course_id == auth.user.course_id).select():
        section_form.append(LABEL(
            INPUT(_name="section_id", _type="radio", _value=section.id),
            section.name,
            _class="radio-inline",
            ))

    section_form.append(INPUT(_type="submit", _value="Filter Students", _class="btn btn-default"))

    joined = db((db.code.sid == db.auth_user.username) & (db.section_users.auth_user == db.auth_user.id))
    q = joined((db.code.course_id == auth.user.course_id) & (db.code.acid == acid))

    if section_form.accepts(request.vars, session, keepvalues=True) and section_form.vars.section_id != "":
        q = q(db.section_users.section == section_form.vars.section_id)

    rset = q.select(
        db.code.acid,
        db.code.sid,
        db.code.grade,
        db.code.id,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.code.comment,
        distinct = db.code.sid,
        orderby = db.code.sid|db.code.timestamp,
        )
    return dict(
        acid = acid,
        sid = sid,
        section_form = section_form,
        solutions=rset,
        course_id=course.course_name
        )


@auth.requires(lambda: verifyInstructorStatus(auth.user.course_name, auth.user), requires_login=True)
def showlog():
    course = db(db.courses.id == auth.user.course_id).select().first()
    grid = SQLFORM.grid(
        (db.useinfo.course_id==course.course_name) & (db.useinfo.timestamp >= course.term_start_date),
        fields=[db.useinfo.timestamp,db.useinfo.sid, db.useinfo.event,db.useinfo.act,db.useinfo.div_id],
        editable=False,
        deletable=False,
        details=False,
        orderby=~db.useinfo.timestamp,
        paginate=40,
        formstyle='divs')
    return dict(grid=grid,course_id=course.course_name)
    
@auth.requires(lambda: verifyInstructorStatus(auth.user.course_name, auth.user), requires_login=True)
def showlog_advanced():
    course = db(db.courses.id == auth.user.course_id).select().first()
    #grid = ((db.useinfo.course_id==course.course_name) & (db.useinfo.timestamp >= course.term_start_date),
    #db.useinfo.timestamp,db.useinfo.sid, db.useinfo.event,db.useinfo.act,db.useinfo.div_id
    grid = [{'time': row.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 
             'user': row.sid, 
             'event': row.event, 
             'act': row.act, 
             'div_id': row.div_id} for row in db().select(db.useinfo.ALL)]
    return dict(grid=json.dumps(grid),course_id=course.course_name)

@auth.requires(lambda: verifyInstructorStatus(auth.user.course_name, auth.user), requires_login=True)
def studentactivity():
    course = db(db.courses.id == auth.user.course_id).select().first()
    count = db.useinfo.id.count()
    last = db.useinfo.timestamp.max()
    res = db((db.useinfo.course_id==course.course_name) & (db.useinfo.timestamp >= course.term_start_date))\
            .select(db.useinfo.sid,
                    count,
                    last,
                    groupby=db.useinfo.sid,
                    orderby=count)

    return dict(grid=res,course_id=course.course_name)
    
@auth.requires(lambda: verifyInstructorStatus(auth.user.course_name, auth.user), requires_login=True)
def startdate():
    course = db(db.courses.id == auth.user.course_id).select().first()
    if request.vars.startdate:
        date = request.vars.startdate.split('/')
        date = datetime.date(int(date[2]), int(date[0]), int(date[1]))
        course.update_record(term_start_date=date)
        session.flash = "Course start date changed."
        redirect(URL('admin','index'))
    else:
        current_start_date = course.term_start_date.strftime("%m/%d/%Y")
        return dict(startdate=current_start_date)

@auth.requires(lambda: verifyInstructorStatus(auth.user.course_name, auth.user), requires_login=True)
def rebuildcourse():
    if not request.vars.projectname or not request.vars.startdate:
        course = db(db.courses.course_name == auth.user.course_name).select().first()
        curr_start_date = course.term_start_date.strftime("%m/%d/%Y")
        return dict(curr_start_date=curr_start_date, confirm=True)
    else:
        # update the start date
        course = db(db.courses.id == auth.user.course_id).select().first()
        date = request.vars.startdate.split('/')
        date = datetime.date(int(date[2]), int(date[0]), int(date[1]))
        course.update_record(term_start_date=date)
        
        # run_sphinx in defined in models/scheduler.py
        row = scheduler.queue_task(run_sphinx, timeout=300, pvars=dict(folder=request.folder,
                                                                       rvars=request.vars,
                                                                       application=request.application,
                                                                       http_host=request.env.http_host))
        uuid = row['uuid']


        course_url=path.join('/',request.application,'static', request.vars.projectname, 'index.html')

        return dict(confirm=False,
                    task_name=uuid,
                    course_url=course_url)

#@auth.requires_membership('instructor')
def buildmodulelist():
    import os.path
    import re
    db.modules.truncate()
    
    def procrst(arg, dirname, names):
        rstfiles = [x for x in names if '.rst' in x]
        
        for rf in rstfiles:
            found = 0
            openrf = open(os.path.abspath(os.path.join(dirname,rf)))
            for line in openrf:
                if 'shortname::' in line:
                    first,shortname = line.split('::')
                    found += 1
                if 'description::' in line:
                    first,description = line.split('::')
                    found += 1
                if found > 1:
                    break
            if found > 1:
                dirs = dirname.split('/')
                db.modules.insert(shortname=shortname.strip(),
                                  description=description.strip(),
                                  pathtofile=os.path.join(dirs[-1],rf))


    compthink_sources = os.path.join(request.folder, 'books', 
                                     'compthink', '_sources')
    os.path.walk(compthink_sources,procrst,None)
    
    session.flash = 'Module Database Rebuild Finished'
    redirect('/%s/admin'%request.application)



def build_exercises():
    import os.path
    import re
    db.modules.truncate()
    
    def procrst(arg, dirname, names):
        rstfiles = [x for x in names if '.rst' in x]
        
        chapter = dirname.replace('\\','/').split('/')[-1]
        directive_pattern = re.compile('^\.\.\s*(.*)::\s*(.*)')
        field_pattern = re.compile('\s+:(.*?):(.*)')
        prior_blank = False
        print chapter
        for rf in rstfiles:
            subchapter = rf.split('.')[0]
            openrf = open(os.path.abspath(os.path.join(dirname,rf)))
            number = 0
            search_status = 'nothing'
            fields = {}
            key, value, body = None, None, ""
            prior_white_index = None
            for line in openrf:
                if prior_blank and line.lstrip() == line and search_status != 'nothing':
                    if key:
                        fields[key] = value
                    print type, name, fields, body[:20].replace('\n', '\\n'), len(body), body.count('\n')
                    body = ''
                    prior_white_index = None
                    key, value = None, None
                    fields = {}
                    search_status = 'nothing'
                    
                if search_status == 'nothing':
                    matches = directive_pattern.findall(line)
                    if matches:
                        type, name = matches[0]
                        search_status = 'directive_found'
                elif search_status == 'directive_found':
                    matches = field_pattern.findall(line)
                    white_index = len(line) - len(line.lstrip())
                    if matches:
                        if key:
                            fields[key] = value
                        key, value = matches[0]
                    elif line.strip():
                        if key:
                            if white_index >= prior_white_index:
                                body += line.lstrip()
                            else:
                                value += line.lstrip()
                        else:
                            body += line.lstrip()
                    prior_blank = ("" == line.strip())
                    if line.strip():
                        prior_white_index = min(prior_white_index, white_index)
            if search_status == 'directive_found':
                print "Extra", type, name, fields, body[:20].replace('\n', '\\n'), len(body), body.count('\n')
                """if ':submission:' in line:
                    cohort = 'cohort' in line
                    number += 1
                    existing = db((db.exercises.chapter==chapter) &
                                  (db.exercises.subchapter==subchapter) &
                                  (db.exercises.div_id==name))
                    print "Deleting", existing
                    existing.delete()
                    db.commit()
                    print "Adding", chapter, subchapter, name
                    db.exercises.insert(chapter=chapter,
                                        subchapter=subchapter,
                                        type=type,
                                        cohort=cohort,
                                        number=number,
                                        div_id=name)"""

    compthink_sources = os.path.join(request.folder, 'books', 
                                     'compthink', '_sources')
    os.path.walk(compthink_sources,procrst,None)    
    session.flash = 'Module Database Rebuild Finished'
    #redirect('/%s/admin'%request.application)