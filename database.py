from sqlalchemy import Text
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class StoreStatus(db.Model):
    id = db.Column(db.Integer, db.Sequence('store_status_id_seq'), primary_key = True, autoincrement=True)
    store_id = db.Column(db.Integer, nullable = False)
    status = db.Column(db.String(10), nullable = False)
    timestamp_utc = db.Column(db.String(50), nullable = False)


class BusinessHours(db.Model):
    id = db.Column(db.Integer, db.Sequence('business_hours_id_seq'), primary_key = True, autoincrement=True)
    store_id = db.Column(db.Integer, nullable = False)
    day_of_week = db.Column(db.Integer, nullable = False)
    start_time_local = db.Column(db.String(50), nullable = False)
    end_time_local = db.Column(db.String(50), nullable = False)


class StoreTimezone(db.Model):
    id = db.Column(db.Integer, db.Sequence('store_timezone_id_seq'), primary_key = True, autoincrement=True)
    store_id = db.Column(db.Integer, nullable = False)
    timezone_str = db.Column(db.String(50), nullable = False)


class Report(db.Model):
    id = db.Column(db.String(36), primary_key = True)
    status = db.Column(db.String(10), nullable = False)
    error_msg = db.Column(db.String(1000), nullable = True)
    csv_file_path = db.Column(db.String(255), nullable=True)
