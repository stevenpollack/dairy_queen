class Showtime(datetime.datetime):
    """
    to extend datetime.time we have to override the __new__ function.
    Overriding the __init__ just yells at you.
    See: http://stackoverflow.com/questions/27430269/python-how-to-extend-datetime-timedelta
    """

    def __new__(cls, time, date=None, time_format='%H:%M', date_format='%Y-%m-%d'):
        if not isinstance(time, str):
            raise TypeError("'time' must be a string")

        if date is not None:
            if not isinstance(date, str):
                raise TypeError("'date' must either be of None or string type")
            ymd = datetime.datetime.strptime(date, date_format)
            year, month, day = ymd.year, ymd.month, ymd.day
        else:
            ymd = gmtime()
            year, month, day = ymd.tm_year, ymd.tm_mon, ymd.tm_mday

        ymd_date = datetime.date(year=year, month=month, day=day)

        showtime = datetime.datetime.strptime(time, time_format)
        showtime_time = datetime.time(hour=showtime.hour, minute=showtime.minute)

        return(datetime.datetime.combine(ymd_date, showtime_time))
