from datetime import timedelta, datetime, date


def get_date_list(startdate: str):
    start_dt = datetime.strptime(startdate, '%Y-%m-%d')
    end_dt = (datetime.now() - timedelta(days=1))

    def daterange(date1, date2):
        for n in range(int ((date2 - date1).days)+1):
            yield date1 + timedelta(n)

    datelist = []
    weekdays = [5,6]
    for dt in daterange(start_dt, end_dt):
        if dt.weekday() not in weekdays:
            datelist.append(dt.strftime("%Y-%m-%d"))
    return datelist