import logging
import sys

from flask import Flask, request, send_file
from http import HTTPStatus
from services import background_executor
from services.report_service import calculate_report, get_report, trigger_report_generation
from database import db, Report

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'csv_files'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

db.init_app(app)
with app.app_context():
    db.create_all()


# Define the endpoint for getting report status and data
@app.route('/get-report', methods=['GET'])
def get_report_status():
    # Get the report ID from the request parameters
    report_id = request.args.get('report_id')
    report = get_report(report_id)
    return {
        "report_id": report_id,
        "status": report.status,
        "error_msg": report.error_msg,
        "csv_file_path": report.csv_file_path
        }


# Define the endpoint for triggering report generation
@app.route('/trigger-report', methods=['POST'])
def trigger_report():
    report_id = trigger_report_generation()
    background_executor.submit(calculate_report, app, report_id)
    return {"report_id": report_id}, HTTPStatus.ACCEPTED


@app.route('/download-csv', methods=['GET'])
def download_csv():
    path_to_csv = request.args.get("csv_path")
    return send_file(path_to_csv, as_attachment=True)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
  