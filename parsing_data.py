import csv
from database import db, BusinessHours, StoreStatus, StoreTimezone

from app import app


def parse_csv_file(filename, model):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader) # skip header
        with app.app_context():
            for row in reader:
                record = model(
                    **dict(zip([column.name for column in list(model.__table__.columns)[1:]], row)))
                db.session.add(record)
            db.session.commit()


def parse_store_status_csv():
    parse_csv_file('csv_files/store_status.csv', StoreStatus)


def parse_business_hours_csv():
    parse_csv_file('csv_files/business_hours.csv', BusinessHours)


def parse_store_timezone_csv():
    parse_csv_file('csv_files/store_timezone.csv', StoreTimezone)

if __name__ == '__main__':
    parse_store_status_csv()
    parse_business_hours_csv()
    parse_store_timezone_csv()
