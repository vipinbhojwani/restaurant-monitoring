import csv
import logging
import traceback

from utils import asdict

from database import db, Report, BusinessHours, StoreStatus, StoreTimezone
from services import background_executor
from services.calculate_report_service import calculate_report_statuses
from utils import generate_random_id

TRIGGERED_STATUS = 'Running'
COMPLETED_STATUS = 'Complete'
FAILED_STATUS = 'Failed'

logger = logging.getLogger(__name__)

def get_report(report_id):
    report = Report.query.filter_by(id=report_id).first()
    return report


def calculate_report(app, report_id):
    with app.app_context():
        report = get_report(report_id)
        logger.info(f"Calculating report for report-id: {report_id}")
        try:
            assert report is not None
            filepath = f'csv_reports/report-{report_id}.csv'
            logger.info(f"Writing report for report-id: {report_id} in filepath: {filepath}")
            with open(filepath, 'w', newline='') as csvfile:
                fieldnames = [
                    'store_id', 'uptime_last_hour(in minutes)', 'uptime_last_day(in hours)',
                    'uptime_last_week(in hours)', 'downtime_last_hour(in minutes)', 
                    'downtime_last_day(in hours)',
                    'downtime_last_week(in hours)'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                business_hour_rows_for_distinct_store_id = BusinessHours.query.distinct(BusinessHours.store_id).all()
                store_ids = list(set([bh.store_id for bh in business_hour_rows_for_distinct_store_id])) # List[str]
                
                for store_id in store_ids:
                    business_hour_rows = BusinessHours.query.filter_by(store_id=store_id).all()
                    business_hours = [asdict(business_hour_row) for business_hour_row in business_hour_rows]

                    store_status_rows = StoreStatus.query.filter_by(store_id=store_id).all()
                    store_statuses = [asdict(store_status_row) for store_status_row in store_status_rows]
                    
                    store_timezone = StoreTimezone.query.filter_by(store_id=store_id).first()
                    timezone_str = store_timezone.timezone_str if store_timezone is not None else 'America/Chicago'

                    store_result = calculate_report_statuses(store_id, business_hours=business_hours, statuses=store_statuses, timezone_str=timezone_str)
                    writer.writerow(store_result)
            logger.info(f"Writing report for report-id: {report_id} finished")
            report.status = COMPLETED_STATUS
            report.csv_file_path = f"{filepath}"
        except Exception as e:
            report.error_msg = str(e)
            report.status = FAILED_STATUS
            logger.error(f"Calculation failed for Report with id: {report_id}")
            traceback.print_exc()
        finally:
            try:
                db.session.add(report)
                db.session.commit()
            except Exception as e:
                logger.error(f"Status update failed for Report with id: {report_id}")
                traceback.print_exc()


def trigger_report_generation():
    report_id = generate_random_id()
    report = Report(id=report_id, status=TRIGGERED_STATUS)
    db.session.add(report)
    db.session.commit()

    return report_id
