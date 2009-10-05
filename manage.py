from werkzeug import script
from exmrss import application, db

def make_app():
    return application

def make_shell_locals():
    from sqlalchemy.orm import create_session
    app = make_app()
    return {"db_engine": app.db_engine, "sess": create_session(app.db_engine),
            "app": app, "metadata": db.metadata}

action_runserver = script.make_runserver(make_app, use_reloader=True)
action_shell = script.make_shell(make_shell_locals)

if __name__ == "__main__":
    script.run()
