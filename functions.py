from datetime import datetime
from db import db


def log_activity(table_name, **kwargs):
    try:
        new_activity_log = table_name(**kwargs, log_date=datetime.now())
        db.session.add(new_activity_log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e


def attendance_log_activity(table_name, location, **kwargs):
    try:
        new_activity_log = table_name(**kwargs, log_date=datetime.now(), log_location=location)
        db.session.add(new_activity_log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
