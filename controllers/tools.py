def index():
    return A('Rebuild', _href=URL('rebuild'))

def status():
    total_log = ""
    with open("book_build.log", "r") as log:
        total_log += log.read()
    with open("applications/dev/build_compthink.log", "r") as log:
        total_log += log.read()
    return PRE(total_log)
    
def build_chapters():    
    # Clear out the old chapters
    current_compthink_chapters = db(db.chapters.course_id == 2)
    current_compthink_chapters.delete()
    db.commit()
    
    # Build up new list of chapters
    with open("applications/runestone/static/compthink/index.html", "r") as index_page:
        index_page = index_page.read()
    #regex for parsing html is evil, but proper parsing would take longer and
    # be as imprecise, not to mention more complicated!
    import re
    output = P()
    links = re.findall('(?:<h\d>(.*)<a.*href="#(.*?)")' # Match up the chapter names
                       '|' # Or match up the section names
                       '(?:<li class="toctree-.*"reference internal" href="(.*?)">(.*?)</a></li>)',
                       index_page)
    # Auto-generated code gives us some assumptions:
    #   * Always starts with a chapter, and the sections follow its chapters, so
    #     we can assume the previous chapter_name was the chapter
    for chapter_name, chapter_label, sub_url, sub_name in links:
        if chapter_name and chapter_label:
            last_chapter_name, last_chapter_label = chapter_name, chapter_label
            output += P(chapter_name + ":" + chapter_label)
        else:
            if '/' in sub_url:
                sub_label = sub_url.split('/')[1].split('.')[0]
            else:
                sub_label = sub_url.split('.')[0]
            output += P(" ::: ".join((last_chapter_name, last_chapter_label, sub_name, sub_label)))
    return output
    
    #result = "Adding Chapter Info to DB"
    #for chapter in subChapD:
    #    print chapter
    #    currentRowId = db.chapters.insert(chapter_name=chapTitles[chapter],course_id=course_id,chapter_label=chapter)
    #    for subchaptername in subChapD[chapter]:
    #        db.sub_chapters.insert(sub_chapter_name=unCamel(subchaptername),
    #                               chapter_id=currentRowId,
    #                               sub_chapter_label=subchaptername)
    #    db.commit()

def rebuild():
    with open("book_build.log", "w") as log:
        import os,sys
        import json
        from subprocess import call
        data = dict(request.vars.items())
        ref = data.get("ref", None)
        if ref is None:
            log.write("No ref given. Only:" + repr(data) + "\n")
        elif ref == "refs/heads/dev":
            call(["/users/acbart/web2py/build_dev.sh"], stdout=log)
        elif ref == "refs/heads/production":
            call(["/users/acbart/build_prod.sh"], stdout=log)
        else:
            log.write("Given: " + repr(data) + "\n")
        log.write("Completed.")
        return ref
