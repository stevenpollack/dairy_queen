import warnings
from time import gmtime
import datetime
import json
from operator import attrgetter # this is for sorting
import collections

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
    """A Movie is an object that stores information for a particular movie (assumed
    to be played in a particular theatre). As in the real-world, a movie has "showtimes",
    the times when its theatre is screening it, a "name", and a "runtime" (its duration in
    minutes).

    Parameters
    ----------
    name: a string.
    runtime: a non-negative integer. Represents the duration of the movie, in minutes.
    showtime: a string to be cast to a datetime object, representing when the movie starts.

    Returns
    -------
    Movie: ...
    """
    def __init__(self, name, runtime, showtime, showtime_format='%H:%M'):
        if runtime <= 0:
            raise ValueError('runtime must be a positive integer')

        self.start = datetime.datetime.strptime(showtime, showtime_format)

        self.runtime = datetime.timedelta(minutes=runtime)
        self.name = name

        self.end = self.start + self.runtime

    def __str__(self):
        output =  '%s (%s min): showing from %s to %s' % \
                  (self.name, str(self.runtime.total_seconds() / 60), self.start, self.end)
        return(output)

    def __repr__(self):
        output = "Movie(name=%r, runtime=%r, start=%r, end=%r)" % (self.name, self.runtime, self.start, self.end)
        return(output)


class Theatre:
    """ Theatre object

    Parameters
    ------------
    name : a string indicating the name of the theatre.
    program : an iterable containing entries which must have "name", "runtime",
        and "showtimes" as keys that can be retrieved via a get()-method.

    Returns
    -------
    Theatre : a Theatre object which has properties "name" (str) and "program" ([Movie]).
    """

    double_dips = None

    def __init__(self, name, program):

        if isinstance(name, str):
            self.name = name
        else:
            raise TypeError("'name' must be a string")

        self.program = []
        # follow duck typing:
        # assume program is anything that can be coerced into a list
        # and then iterate over the coerced list
        for movie in list(program):
            for showtime in list(movie.get('showtimes')):
                try:
                    self.program.append(
                        Movie(name=movie.get('name'),
                              runtime=movie.get('runtime'),
                              showtime=showtime)
                    )
                except ValueError:
                    warnings.warn(movie.get('name') + "could not be coerced to a Movie due to bad runtime...")

    def load_program(self, dicts):
        pass

    def __str__(self):
        output = self.name + "\n\nProgram:\n"
        output += '\n'.join([movie.__str__() for movie in self.program]) + "\n"
        return(output)

    def __repr__(self):
        output = "Theatre(name=%r, program=%r)" % (self.name, self.program)
        return(output)

    def calculate_double_dips(self, max_waiting_time=45, max_overlap_time=30):

        max_waiting_time = datetime.timedelta(minutes = max_waiting_time)
        max_overlap_time = datetime.timedelta(minutes = max_overlap_time)

        def filter_program(movie):
            output = []
            # filter out all movies that are too "far away" or too "close".
            for x in self.program:
                if movie.name != x.name and movie.end <= x.start + max_overlap_time and x.start <= movie.end + max_waiting_time:
                    output.append(x)
            return(output)

        # SO- flatten arbirtary list:
        # http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python#2158532
        # this yields a GENERATOR, not a list...
        def flatten(l):
            for el in l:
                if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
                    for sub in flatten(el):
                        yield sub
                else:
                    yield el

        def find_all_paths(movie):

            eligible_movies = filter_program(movie)

            # if no movies pass the filter, we're done
            # return the terminal node as a list so that
            # we can prepend future movies to this using `insert`.
            if len(eligible_movies) == 0:
                return([movie])
            else:
            # otherwise, we recursively branch out and explore
            # all the potential paths
                collected_paths = []
                for eligible_movie in eligible_movies:
                    paths = find_all_paths(eligible_movie)
                    paths = list(flatten(paths)) # list out generator... maybe this isn't a smart idea
                    paths.insert(0, movie)
                    collected_paths.append(paths)
                return(collected_paths)

        # sort program in ASC start-time...
        self.program.sort(key = attrgetter('start'))

        self.double_dips = []

        for movie in self.program:
            self.double_dips.append(find_all_paths(movie))

        return(double_dips)

if (__name__ == "__main__"):
    #times = ["9:20", "17:20"]
    #print(Movie('her', 15, times))
    json_dict = json.load(open('test.json'))
    x = Theatre(name = json_dict[0]['name'], program = json_dict[0]['program'])
    x.calculate_double_dips()

    for dict in json_dict:
        print(Theatre(name = dict['name'], program=dict['program']).calculate_double_dips())