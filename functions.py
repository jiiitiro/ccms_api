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
