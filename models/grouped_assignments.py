import datetime

def pct2pts(x):
    return "%.2f" % (100*x)

class Grade(object):
    """Grade of one user for either a collection of assignments, or for the whole course"""
    def __init__(self):
        self.weight = 1
        self.scores = []
        self.assignment_scores = []
    
    def points(self):
        self.scores.sort()
        if len(self.scores) > self.assignments_count - self.assignments_dropped:
            # too many grades; drop lowest
            return sum(self.scores[self.assignments_dropped:])
        else:
            return sum(self.scores)
    
    def assignment_points(self):
        self.assignment_scores.sort()
        if len(self.scores) > self.assignments_count - self.assignments_dropped:
            # too many grades; drop lowest assignment
            return sum(self.assignment_scores[self.assignments_dropped:])
        else:
            return sum(self.assignment_scores)
            
    
    def current(self):
        if self.possible == 0:
            return 0
        points = float(self.points())/self.possible
        return points*self.weight

    def projected(self):
        if self.assignment_points() == 0:
            return 0
        points = float(self.points())/self.assignment_points()
        return points*self.weight

    def points_after_drops(self):
        self.scores.sort()
        return sum(self.scores[self.assignments_dropped:])
    def assignment_points_after_drops(self):
        self.assignment_scores.sort()
        return sum(self.assignment_scores[self.assignments_dropped:])

    def max(self):
        # this is more complicated because of the "best k of n" scoring
        
        if self.possible == 0:
            return 0
        remaining = self.possible - self.assignment_points_after_drops()
        if remaining < 0:
            remaining = 0
        points = (self.points_after_drops() + remaining)/self.possible
        return points * self.weight

    def percent(self, points=None, total=None):
        if points == None:
            points = self.points()
        if total == None:
            total = self.assignment_points()
        if total == 0:
            return "0%"
        percent = round((points / total) * 100)
        return "%d%%" % (percent)

class CourseGrade(Grade):
    def __init__(self):
        super(CourseGrade, self ).__init__()
        self.points = 0
        self.projected_pts = 0
        self.max_pts = 0
        
    def current(self):
        return self.points
    
    def projected(self):
        return self.projected_pts
    
    def max(self):
        return self.max_pts

def student_grade(user=None, course=None, assignment_type=None):
    grade = Grade()
    if not user or not course or not assignment_type:
        return grade

    # Check assignment type weight before setting it in case its None
    if assignment_type.weight != None:
        grade.weight = assignment_type.weight
    if assignment_type.points_possible != None:
        grade.possible = assignment_type.points_possible
    if assignment_type.assignments_count:
        grade.assignments_count = int(assignment_type.assignments_count)
    if assignment_type.assignments_dropped:
        grade.assignments_dropped = int(assignment_type.assignments_dropped) 

    assignments = db(db.assignments.id == db.grades.assignment)
    assignments = assignments(db.assignments.course == course.id)
    assignments = assignments(db.grades.auth_user == user.id)
    assignments = assignments(db.assignments.released == True)
    assignments = assignments(db.assignments.assignment_type == assignment_type.id)
    assignments = assignments.select(
        db.assignments.ALL,
        db.grades.ALL,
        orderby=db.assignments.name,
        )
    for row in assignments:
        grade.scores.append(row.grades.score)
        grade.assignment_scores.append(row.assignments.points)
    return grade

db.define_table('assignment_types',
    Field('name', 'string'),
    Field('grade_type', 'string', default="additive", requires=IS_IN_SET(['additive', 'checkmark', 'use'])),
    Field('weight', 'double', default=1.0),
    Field('points_possible','integer', default=0),
    Field('assignments_count', default=0),
    Field('assignments_dropped', default=0),
    format='%(names)s',
    migrate='runestone_assignment_types.table',
    )

db.define_table('assignments',
    Field('course', db.courses),
    Field('assignment_type', db.assignment_types, requires=IS_EMPTY_OR(IS_IN_DB(db, 'assignment_types.id', '%(name)s'))),
    Field('name', 'string'),
    Field('points', 'integer'),
    Field('threshold', 'integer', default=1),
    Field('released', 'boolean'),
    format='%(name)s',
    migrate='runestone_assignments.table'
    )

class score(object):
    def __init__(self, acid=None, points=0, comment="", user=None):
        self.acid = acid
        self.user = user
        self.points = points
        if type(self.points) not in [float, int]:
            # would be nice to flag error here
            self.points = 0 
        self.comment = comment

def canonicalize(div_id):
    if ".html" in div_id:
        full_url = div_id
        # return canonical url, without #anchors
        if full_url.rfind('#') > 0:
            full_url = full_url[:url.rfind('#')]
        full_url = full_url.replace('/runestone/static/pip/', '')
        return full_url
    else:
        return div_id
class Session(object):
    def __init__(self, start, end = None, assignment = None):
        self.start = start
        self.end = end
        self.count = 1
        self.assignment = assignment

def get_deadline(assignment, user):
    section = section_users(db.auth_user.id == user.id).select(db.sections.ALL).first()
    q = db(db.deadlines.assignment == assignment.id)
    if section:
        q = q((db.deadlines.section == section.id) | (db.deadlines.section==None))
    else:
        q = q(db.deadlines.section==None)
    dl = q.select(db.deadlines.ALL, orderby=db.deadlines.section).first()
    if dl:
        return dl.deadline  #a datetime object
    else:
        return None

def assignment_get_engagement_time(assignment, user, preclass):
    # get all the divids for this assignment
    divids = [row.acid for row in db(db.problems.assignment == assignment.id).select(db.problems.acid)]
    
    # get all the activities for this user
    # could probably simplify and get a reasonable approximation by just retrieving the activities for this assignment; FUTURE WORK
    q = db(db.useinfo.sid == user.username)
    if preclass:
        dl = get_deadline(assignment, user)
        if dl:
            q = q(db.useinfo.timestamp < dl)

    activities = q.select(db.useinfo.div_id, db.useinfo.timestamp, orderby = db.useinfo.timestamp)
    sessions = []
    THRESH = 600
    prev = None
    for current in activities:
        div_id = canonicalize(current.div_id)
        if prev and canonicalize(prev.div_id) in divids:
            if div_id not in divids or (current.timestamp - prev.timestamp).total_seconds() > THRESH:
                # close previous session
                if len(sessions) > 0 and not sessions[-1].end:
                    sessions[-1].end = prev.timestamp + datetime.timedelta(seconds=30)
            else:
                # add to activities count for previous session
                sessions[-1].count += 1
        if div_id in divids:
            if len(sessions) == 0 or sessions[-1].end:
                sessions.append(Session(current.timestamp))
        prev = current
    if len(sessions) > 0 and not sessions[-1].end:
        # close out last session
        sessions[-1].end = prev.timestamp + datetime.timedelta(seconds=30)
    total_time = sum([(s.end-s.start).total_seconds() for s in sessions])
    return total_time

def assignment_get_use_scores(assignment, problem=None, user=None, section_id=None, preclass=True):
    scores = []
    if problem and user:
        pass
    elif problem:
        pass
    elif user:
        q =  db(db.useinfo.div_id == db.problems.acid)(db.problems.assignment == assignment.id)(db.useinfo.sid == user.username)
        if preclass:
            dl = get_deadline(assignment, user)
            if dl:
                q = q(db.useinfo.timestamp < dl)       
        attempted_problems = q.select(db.problems.acid)
        for problem in db(db.problems.assignment == assignment.id).select(db.problems.acid):
            if ".html" in problem.acid:
                # don't include opening the page as a problems they can attempt or not;
                # they are included as problems so that total time on session prep
                # is calculated correctly
                continue
            matches = [x for x in attempted_problems if x.acid == problem.acid]
            points = 0
            if len(matches) > 0:
                points = 1
            scores.append(score(
                points = points,
                acid = problem.acid,
                user = user,
                ))
    else:
        pass
    return scores

def get_all_times_and_activity_counts(course):
    ## get mapping from problem names (divids) to assignments, and count of problems per assignment
    p2a = {}
    act_per_ass = {}
    deadlines = {}
    for p in db(db.assignment_types.id == db.assignments.assignment_type)(db.assignment_types.grade_type == 'use')(db.problems.assignment == db.assignments.id).select():
        p2a[canonicalize(p.problems.acid)] = p.assignments.id
        act_per_ass[p.assignments.id] = act_per_ass.get(p.assignments.id, 0) + 1
    def times(assignment, pre_deadline=False):
        sessions = assignment['sessions']
        if pre_deadline and 'deadline' in assignment and assignment['deadline']:
            dl = assignment['deadline']
            sessions = [s for s in sessions if s.start < dl]
        return sum([(s.end-s.start).total_seconds() for s in sessions])
    def count(assignment, pre_deadline=False):
        acts = assignment['activities'].values()
        if pre_deadline and 'deadline' in assignment and assignment['deadline']:
            dl = assignment['deadline']
            acts = [a for a in acts if a < dl]
        return len(acts)
    def name(assignment_id):
        return db.assignments(assignment_id).name
    def get_deadline(assignment_id, user_id):
        section = section_users(db.auth_user.registration_id == user_id).select(db.sections.ALL).first()
        q = db(db.deadlines.assignment == assignment_id)
        if section:
            q = q((db.deadlines.section == section.id) | (db.deadlines.section==None))
        else:
            q = q(db.deadlines.section==None)
        dl = q.select(db.deadlines.ALL, orderby=db.deadlines.section).first()
        if dl:
            return dl.deadline  #a datetime object
        else:
            return None
    class User_data:
        def __init__(self, user_id):
            self.user_id = user_id
            self.assignments = {}
            ## {'assignment_id' : {'deadline': datetime, 'sessions' : [instances of Session], 'activities': {div_id: datetime}}}
        def add_session(self, s, div_id):
            a = p2a[div_id]
            if a not in self.assignments:
                self.assignments[a] = {'sessions': [], 'activities': {}, 'deadline': get_deadline(a, self.user_id)}
            self.assignments[a]['sessions'].append(s)
        def add_activity(self, div_id, timestamp):
            a = p2a[div_id]
            if a not in self.assignments:
                self.assignments[a] = {'sessions': [], 'activities': {}, 'deadline': get_deadline(a, self.user_id)}
            if div_id not in self.assignments[a]['activities']:
                self.assignments[a]['activities'][div_id] = timestamp
        def csv_dict(self):
            ret = {}
            ret['user_id'] = self.user_id
            for a in self.assignments:
                nm = name(a)
                ret[nm+"_time"] = times(self.assignments[a])
                ret[nm+"_time_pre_deadline"] = times(self.assignments[a], pre_deadline=True)
                ret[nm+"_activities"] = count(self.assignments[a])
                ret[nm+"_activities_pre_deadline"] = count(self.assignments[a], pre_deadline=True)
                ret[nm+"_max_act"] = act_per_ass[a]
            return ret
            
                
    students = db(db.auth_user.course_id == course.id).select(db.auth_user.registration_id)
    all_user_data = {}
    for student in students:
        curr_user = User_data(student.registration_id)        
        ## get all use scores and times for this user
        rows = db(db.useinfo.sid == student.registration_id).select(orderby=db.useinfo.timestamp)
        curr_session = None
        prev_row = None
        THRESH = 600
        for row in rows:
            div_id = canonicalize(row.div_id)
            if div_id not in p2a:
                continue  # ignore activities that aren't associated with any assignment
            curr_user.add_activity(div_id, row.timestamp)
            if curr_session: # see whether to continue it or close it
                if curr_session.assignment == p2a[div_id] and (row.timestamp - prev_row.timestamp).total_seconds() < THRESH:
                    # continue current session if same assignment and not too much time has passed since last activity
                    pass
                else:
                    # close previous session
                    curr_session.end = prev_row.timestamp + datetime.timedelta(seconds=30)
                    curr_session = None
            if not curr_session:
                # start a new one and add it to sessions list for that assignment for current user
                curr_session = Session(row.timestamp, assignment = p2a[div_id])
                curr_user.add_session(curr_session, div_id)
            prev_row = row
        if curr_session and not curr_session.end:
            # close very last session
            curr_session.end = prev_row.timestamp + datetime.timedelta(seconds=30)
        all_user_data[curr_user.user_id] = curr_user.csv_dict()
    return all_user_data

def assignment_get_scores(assignment, problem=None, user=None, section_id=None, preclass=True):
    assignment_type = db(db.assignment_types.id == assignment.assignment_type).select().first()
    if assignment_type and assignment_type.grade_type == 'use':
        return assignment_get_use_scores(assignment, problem, user, section_id, preclass)
    scores = []
    if problem and user:
        pass
    elif problem:
        grades = db(db.code.sid == db.auth_user.username)(db.code.acid == problem).select(
            db.code.ALL,
            db.auth_user.ALL,
            orderby=db.code.sid | db.code.timestamp,
            distinct=db.code.sid,
            )
        for g in grades:
            scores.append(score(
                points=g.code.grade,
                comment=g.code.comment,
                acid=problem,
                user=g.auth_user,
                ))
    elif user:
        q = db(db.problems.acid == db.code.acid)
        q = q(db.problems.assignment == assignment.id)
        q = q(db.code.sid == user.username)
        grades = q.select(
            db.code.acid,
            db.code.grade,
            db.code.comment,
            db.code.timestamp,
            orderby=db.code.acid | db.code.timestamp,
            distinct=db.code.acid,
            )
        for g in grades:
            scores.append(score(
                points=g.grade,
                comment=g.comment,
                acid=g.acid,
                user=user,
                ))
    else:
        grades = db(db.grades.assignment == assignment.id).select(db.grades.ALL)
        for g in grades:
            scores.append(score(
                points=g.score,
                user=g.auth_user,
                ))
    return scores
db.assignments.scores = Field.Method(lambda row, problem=None, user=None, section_id=None, preclass=True: assignment_get_scores(row.assignments, problem, user, section_id, preclass))
db.assignments.time = Field.Method(lambda row, user=None, preclass=True: assignment_get_engagement_time(row.assignments, user, preclass))

def assignment_set_grade(assignment, user):
    # delete the old grades; we're regrading
    db(db.grades.assignment == assignment.id)(db.grades.auth_user == user.id).delete()

    assignment_type = db(db.assignment_types.id == assignment.assignment_type).select().first()
    if not assignment_type:
        # if we don't know how to grade this assignment, don't grade the assignment.
        return 0

    points = 0.0
    if assignment_type.grade_type == 'use':
        checks = len([p for p in assignment_get_scores(assignment, user=user, preclass=False) if p.points > 0])
        time = assignment_get_engagement_time(assignment, user, preclass=True)
        if checks >= assignment.threshold or time > 20*60:
            # if enough checkmarks or enough time
            points = assignment.points
        else:
            points = 0
    elif assignment_type.grade_type == 'checkmark':
        checks = sum([p.points for p in assignment.scores(user=user) if p.points])
        # threshold grade
        if checks >= assignment.threshold:
            points = assignment.points
        else:
            points = 0
    else:
        # they got the points they earned
        points = sum([p.points for p in assignment.scores(user=user)])
        
    db.grades.insert(
        auth_user=user.id,
        assignment=assignment.id,
        score=points,
        )
    return points
db.assignments.grade = Field.Method(lambda row, user: assignment_set_grade(row.assignments, user))

def assignment_release_grades(assignment, released=True):
    # update problems
    assignment.released = True
    assignment.update_record()
    return True
db.assignments.release_grades = Field.Method(lambda row, released=True: assignment_release_grades(row.assignments, released))

db.define_table('problems',
    Field('assignment', db.assignments),
    Field('acid', 'string'),
    migrate='runestones_problems.table',
    )

db.define_table('grades',
    Field('auth_user', db.auth_user),
    Field('assignment', db.assignments),
    Field('score', 'double'),
    migrate='runestone_grades.table',
    )

db.define_table('deadlines',
    Field('assignment', db.assignments, requires=IS_IN_DB(db, 'assignments.id', db.assignments._format)),
    Field('section', db.sections, requires=IS_EMPTY_OR(IS_IN_DB(db, 'sections.id', '%(name)s'))),
    Field('deadline', 'datetime'),
    migrate='runestone_deadlines.table',
    )
