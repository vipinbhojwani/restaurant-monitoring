from datetime import datetime, timedelta
import pytz

from collections import defaultdict


def parse_time_str(date_str, timezone_str):
    date_format = '%H:%M:%S'

    dt = datetime.strptime(date_str, date_format)
    tz = pytz.timezone(timezone_str)
    dt = tz.localize(dt)

    return dt

def get_day_of_week_and_local_time(timestamp_utc, timezone_str):
    timestamp_utc = timestamp_utc[:19]
    tz = pytz.timezone(timezone_str)
    utc_time = datetime.strptime(timestamp_utc, "%Y-%m-%d %H:%M:%S")
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(tz)

    return local_time.weekday(), parse_time_str(timestamp_utc[-8:], timezone_str)


def calculate_report_statuses(store_id, business_hours, statuses, timezone_str):
    # each event is a tuple of timestamp and event_type
    day_to_events = {}

    for business_hours_row in business_hours:
        open_time = parse_time_str(business_hours_row['start_time_local'], timezone_str)
        close_time = parse_time_str(business_hours_row['end_time_local'], timezone_str)
        day_of_week = int(business_hours_row['day_of_week'])

        day_to_events[day_of_week] = day_to_events.get(day_of_week, [])
        day_to_events[day_of_week] += [(open_time, 'open'), (close_time, 'closed')]
    
    # assume store is open if no business hours for a day are provided
    for day_of_week in range(7):
        if day_of_week not in day_to_events:
            day_to_events[day_of_week] = [
                (parse_time_str('00:00:00', timezone_str), 'open'),
                (parse_time_str('23:59:59', timezone_str), 'closed')
                ]
    
    for store_status in statuses:
        event_status = store_status['status']
        day_of_week, event_time = get_day_of_week_and_local_time(store_status['timestamp_utc'], timezone_str)
        day_to_events[day_of_week].append((event_time, event_status))
    
    day_of_week_to_uptime_downtime = {}
    uptime_last_week = timedelta(0)
    downtime_last_week = timedelta(0)
    for day_of_week in range(7):
        day_to_events[day_of_week].sort()
        
        uptime = timedelta(0)
        downtime = timedelta(0)
        last_business_hour_uptime = timedelta(0)

        last_seen_status = 'active'
        is_open = False
        for event in day_to_events[day_of_week]:
            event_time, event_status  = event
            if event_status == 'open':
                is_open = True
                last_event_time = event_time
            elif event_status == 'inactive':
                if last_seen_status == 'inactive':
                    continue
                if is_open:
                    uptime += event_time - last_event_time 
                last_event_time = event_time
                last_seen_status = 'inactive'
            elif event_status == 'active':
                if last_seen_status == 'active':
                    continue
                if is_open:
                    downtime += event_time - last_event_time
                last_event_time = event_time
                last_seen_status = 'active'
            else:  # closed
                if last_seen_status == 'active':
                    uptime += event_time - last_event_time
                    last_business_hour_uptime = min(timedelta(hours=1), event_time - last_event_time)
                else:
                    downtime += event_time - last_event_time
                    last_business_hour_downtime = min(timedelta(hours=1), event_time - last_event_time)
                    last_business_hour_uptime = timedelta(hours=1) - last_business_hour_downtime
                is_open = False

        day_of_week_to_uptime_downtime[day_of_week] = (uptime, downtime)
        uptime_last_week += uptime
        downtime_last_week += downtime
    
    result = {
        'store_id': store_id,
        'uptime_last_hour(in minutes)': int(last_business_hour_uptime.total_seconds() // 60), 
        'uptime_last_day(in hours)': int(day_of_week_to_uptime_downtime[6][0].total_seconds() // 3600), # last day is Sunday - 6
        'uptime_last_week(in hours)': int(uptime_last_week.total_seconds() // 3600),
        'downtime_last_hour(in minutes)': int(60 - (last_business_hour_uptime.total_seconds() // 60)),
        'downtime_last_day(in hours)': int(day_of_week_to_uptime_downtime[6][1].total_seconds() // 3600), # last day is Sunday - 6
        'downtime_last_week(in hours)': int(downtime_last_week.total_seconds() // 3600),
    }

    return result
