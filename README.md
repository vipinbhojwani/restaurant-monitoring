# Restaurant Monitoring
It is a Python3 and Flask based project to keep records of online/offline duration of restaurants during their business hours, which might be used to ensure whether the restaurant would probably be available for online services.

For Database connections, SQL-Alchemy is used.

## How to Setup?
1. Create a Python virtual environment for an isolated setup
    ```
    python3 -m venv venv
    ```

2. Activate the virtual environment
    ```
    source venv/bin/activate
    ```

3. Install pip dependencies
    ```
    pip install -r requirements.txt
    ```

4. Start the app once. Database gets created when we run the app using
    ```
    python app.py
    ```
    Verify that it's created at `instance/database.db`. SQLite client can be used to verify this.

5. Download and keep CSV files in the folder `csv_files`, named as 
   - `business_hours.csv`
   - `store_status.csv`
   - `store_timezone.csv`
  
6. To Parse and ingest CSV files to database, run:
   ```
    python parsing_data.py
   ```


## Problems in hand
### Report calculation logic 
1. `business_hours` table is used to get all distinct `store-ids`

2. For each store, `business_hours` and `store_statuses` are used to form a event timeline for a day. 
It's done using Python list of tuples where the first value of tuple is event-time and second is event-status

3. Based on this event-timeline `uptime` and `downtime` stats are calculated

4. Result is formed as required for the exercise and can be found at `csv_reports/report-e1096218-3eeb-4293-ad46-88f7666ea750.csv`

### Running background process
After trigger, report-calculation has to happen in background.  `threading` is used for this project to run asynchronous task, but in bigger projects, `Celery` is a better choice.
Celery is a popular scalable task manager for Python projects, that can scale well with different brokers like RabbitMQ

### Writing to CSV
`csv.DictWriter` is used to create and write the result CSV to `csv_reports` directory

## How to Run?
1. Acitvate virtual environment:
   ```
   source venv/bin/activate
   ```

2. Run the app.py
    ```
    python app.py
    ```

It should start server at port 8000 and the apis should be accessible at http://127.0.0.1:8000

## How to test REST APIs?
1. Trigger Report API
   ```
   curl --location --request POST 'http://127.0.0.1:8000/trigger-report'
   ```
   
   Sample response:
   `202 Accepted`
   ```
   {"report_id": "e1096218-3eeb-4293-ad46-88f7666ea750"}
    ```

2. Get Report API
   ```
    curl --location 'http://127.0.0.1:8000/get-report?report_id=e1096218-3eeb-4293-ad46-88f7666ea750'
    ```
    Sample response:
   `200 OK`
   ```
   {
        "csv_file_path": ,
        "error_msg": null,
        "report_id": "e1096218-3eeb-4293-ad46-88f7666ea750",
        "status": "Complete"
    }   
    ```
    
    When it's finished, response has csv_file_path like:
    ```
    {
        "csv_file_path": "csv_reports/report-e1096218-3eeb-4293-ad46-88f7666ea750.csv",
        "error_msg": null,
        "report_id": "e1096218-3eeb-4293-ad46-88f7666ea750",
        "status": "Complete"
    }
    ```
   
3. Download CSV API
    ```
    curl --location 'http://127.0.0.1:8000/download-csv?csv_path=csv_reports%2Freport-e1096218-3eeb-4293-ad46-88f7666ea750.csv'
    ```
    Sample response: `200 OK` with csv file attached `Content-Type: text/csv; charset=utf-8` 
    
    CSV File has following columns:
    ```
    store_id, uptime_last_hour(in minutes), uptime_last_day(in hours), uptime_last_week(in hours), downtime_last_hour(in minutes), downtime_last_day(in hours), downtime_last_week(in hours)
    ```

## Future Work
- Unit tests - Unit tests can be added for a real production application
- Code Refactoring - More modularisation like break into smaller methods and modules can be done, e.g:
    - `calculate_report_service.py` can be modularised further
    - `app.py` setup logging can be moved out to another module
- PEP-8 standards compliance - Tools can be used to ensure Python coding standards is maintained
- Authentication / Authorization on different endpoints

