import warnings
import datetime
from operator import attrgetter # this is for sorting
from .movie import Movie
from .doubledip import DoubleDip

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
    address = None
    json = None

    def __init__(self, name, program, address=None):

        if isinstance(name, str):
            self.name = name
        else:
            raise TypeError("'name' must be a string")

        if address is not None:
            if isinstance(address, str):
                self.address = address
            else:
                raise TypeError("'address' must be a string")

        self.program = []

        # there's a subtle problem with program is a dictionary (or tuple)
        # that's not wrapped in [], so we have to check for that
        if isinstance(program, (tuple, dict)):
            program = [program]
        else:
            # we wrap in a list (since this is idempotent, we shouldn't
            # have issues iterating over it.
            program = list(program)

        for movie in program:
            # movie['showtimes'] can either be a string or [string]
            # so wrap in [] to be safe.
            showtimes = movie.get('showtimes')

            if isinstance(showtimes, str):
                showtimes = [showtimes]
            elif not isinstance(showtimes, list):
                raise TypeError("the 'showtimes' properties of a movie must be a string or list or strings")

            for showtime in showtimes:
                try:
                    self.program.append(
                        Movie(name=movie.get('name'),
                              runtime=movie.get('runtime'),
                              showtime=showtime)
                    )
                except ValueError:
                    warnings.warn(movie.get('name') + " could not be coerced to a Movie due to bad runtime...")

    def __str__(self):
        output = self.name + "\n\nProgram:\n"
        output += '\n'.join([movie.__str__() for movie in self.program]) + "\n"
        return(output)

    def __repr__(self):
        output = "Theatre(name=%r, program=%r)" % (self.name, self.program)
        return(output)

    def to_json(self, max_waiting_time=45, max_overlap_time=30, showtime_format='%H:%M'):
        if self.double_dips is None:
            self.calculate_double_dips(max_waiting_time, max_overlap_time)
            return self.to_json(max_waiting_time, max_overlap_time)

        self.json = {
            'name': self.name,
            'address': self.address,
            'doubleDips': [double_dip.to_json(showtime_format) for double_dip in self.double_dips]
        }

        return self.json


    def calculate_double_dips(self, max_waiting_time=45, max_overlap_time=5):

        max_waiting_time = datetime.timedelta(minutes = max_waiting_time)
        max_overlap_time = datetime.timedelta(minutes = max_overlap_time)

        def filter_program(movie):
            output = []
            # filter out all movies that are too "far away" or too "close".
            for x in self.program:
                if movie.name != x.name and movie.end <= x.start + max_overlap_time and x.start <= movie.end + max_waiting_time:
                    output.append(x)
            return(output)

        def find_all_dips_starting_from(movie):

            # label this movie as visited
            if movie not in visited_movies:
                visited_movies.append(movie)
            else:
                return([])

            eligible_movies = filter_program(movie)

            # if no movies pass the filter, we're done
            # return the terminal node as a list so that
            # we can prepend future movies to this using `insert`.
            if len(eligible_movies) == 0:
                return(DoubleDip(movie))
            else:
            # otherwise, we recursively branch out and explore
            # all the potential paths
                all_dips_from_movie = []
                for eligible_movie in eligible_movies:

                    if eligible_movie in visited_movies:
                        break

                    double_dips = find_all_dips_starting_from(eligible_movie)

                    if isinstance(double_dips, DoubleDip):
                        double_dips.prepend(movie)
                        all_dips_from_movie.append(double_dips)
                    else:
                        # double dips should be a list
                        for double_dip in double_dips:
                            double_dip.flat_prepend(movie)
                            all_dips_from_movie.append(double_dip)

                return(all_dips_from_movie)

        # sort program in ASC start-time...
        self.program.sort(key = attrgetter('start'))

        # create a stack to check if a movie has been visited in the DFS
        visited_movies = []

        self.double_dips = []

        for movie in self.program:

            # dips can either be a single DoubleDip object, or a [DoubleDips].
            # if the latter, we can just + dips to self.double_dips.
            # if the former, +'ing will cast the DoubleDip back down to a movie.
            # This is undesirable for printing purposes later (when we want
            # to convert to JSON).
            dips = find_all_dips_starting_from(movie)

            # if a movie has already been visited, an [] will be returned
            if isinstance(dips, DoubleDip):
                self.double_dips.append(dips)
            else:
                self.double_dips += dips

        return(self.double_dips)
