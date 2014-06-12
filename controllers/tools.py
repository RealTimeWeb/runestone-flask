def index():
    return A('Rebuild', _href=URL('rebuild'))

def status():
    total_log = ""
    with open("book_build.log", "r") as log:
        total_log += log.read()
    with open("applications/dev/build_compthink.log", "r") as log:
        total_log += log.read()
    return PRE(total_log)

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
