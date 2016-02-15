import warnings
from time import gmtime
import datetime

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


class Movie:

    def __init__(self, name, runtime, showtimes):
        if runtime <= 0:
            raise ValueError('runtime must be a positive integer')

        self.runtime = datetime.timedelta(minutes=runtime)
        self.name = name

        self.showtimes = []
        for showtime in showtimes:
            if isinstance(showtime, Showtime):
                self.showtimes.append({
                    'start': showtime,
                    'end': showtime + self.runtime
                })
            elif isinstance(showtime, str):
                showtime = Showtime(showtime)
                self.showtimes.append({
                    'start': showtime,
                    'end': showtime + self.runtime
                })
            else:
                warnings.warn('Tried passing in a showtime that was neither a Showtime nor string... Dropping it from the showtimes.')


    def __str__(self):
        output =  self.name + ' with a runtime of ' + str(self.runtime.total_seconds() / 60) + ' minutes and showings at '
        output += ', '.join([ showtime['start'].__str__() for showtime in self.showtimes])
        return(output)

class Theatre:

    def __init__(self, name, ):
        pass

if (__name__ == "__main__"):
    times = ["9:20", "17:20"]
    print(Movie('her', 15, times))