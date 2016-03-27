import warnings
import datetime
from operator import attrgetter  # this is for sorting
from .movie import Movie
from .doubledip import DoubleDip


class Theatre:
    """ Theatre object

    Parameters
    ------------
    name : a string indicating the name of the theatre.
    showtimes : an iterable containing entries which must have "name", "runtime",
        and "times" as keys that can be retrieved via a get()-method.

    Returns
    -------
    Theatre : a Theatre object which has properties "name" (str) and "showtimes" ([Movie]).
    """

    double_dips = None
    info = None
    json = None

    def __init__(self, name, showtimes, info=None):

        if isinstance(name, str):
            self.name = name
        else:
            raise TypeError("'name' must be a string")

        if info is not None:
            if isinstance(info, str):
                self.info = info
            else:
                raise TypeError("'info' must be a string")

        self.showtimes = []

        # there's a subtle problem with showtimes is a dictionary (or tuple)
        # that's not wrapped in [], so we have to check for that
        if isinstance(showtimes, (tuple, dict)):
            showtimes = [showtimes]
        else:
            # we wrap in a list (since this is idempotent, we shouldn't
            # have issues iterating over it.
            showtimes = list(showtimes)

        for movie in showtimes:
            # movie['times'] can either be a string or [string]
            # so wrap in [] to be safe.
            times = movie.get('times')

            if isinstance(times, str):
                times = [times]
            elif not isinstance(times, list):
                raise TypeError("the 'times' properties of a movie must be a string or list or strings")

            for time in times:
                try:
                    self.showtimes.append(
                        Movie(name=movie.get('name'),
                              runtime=movie.get('runtime'),
                              time=time)
                    )
                except ValueError:
                    warnings.warn(movie.get('name') + " could not be coerced to a Movie due to bad runtime...")

    def __str__(self):
        output = self.name + "\n\nshowtimes:\n"
        output += '\n'.join([movie.__str__() for movie in self.showtimes]) + "\n"
        return (output)

    def __repr__(self):
        output = "Theatre(name=%r, showtimes=%r)" % (self.name, self.showtimes)
        return (output)

    def to_json(self, max_waiting_time=45, max_overlap_time=30, time_format='%H:%M'):
        if self.double_dips is None:
            self.calculate_double_dips(max_waiting_time, max_overlap_time)
            return self.to_json(max_waiting_time, max_overlap_time)

        self.json = {
            'name': self.name,
            'info': self.info,
            'doubleDips': [double_dip.to_json(time_format) for double_dip in self.double_dips]
        }

        return self.json

    def calculate_double_dips(self, max_waiting_time=45, max_overlap_time=5):

        max_waiting_time = datetime.timedelta(minutes=max_waiting_time)
        max_overlap_time = datetime.timedelta(minutes=max_overlap_time)

        def filter_ineligible_future_movies(movie, future_movies):
            # this help function assumes that future_movies already filters out
            # future instances of movie.name.
            output = []

            for x in future_movies:
                # throw out movies that start too early
                if x.start < movie.end - max_overlap_time:
                    continue
                # throw out movies that start too late
                if x.start > movie.end + max_waiting_time:
                    continue
                output.append(x)

            return output

        def find_all_dips_starting_from(movie, future_movies):

            # label this movie as visited
            visited_movies.add(movie)

            # With every recursive call to find_all_dips_starting_from, we need to
            # make sure that any future showings of the movie.name aren't going to
            # sit in the stack of movies that we choose eligible movies from,
            # pruned_showtimes. Basically, we need to setup "perpetual filtration"
            # on pruned_showtimes to stop a double dip from re-introducing the same
            # title down the road.
            pruned_showtimes = [x for x in future_movies if x.name != movie.name]
            eligible_movies = filter_ineligible_future_movies(movie, pruned_showtimes)

            # if no movies pass the filter, we're done
            # return the terminal node as a list so that
            # we can prepend future movies to this using `insert`.
            if len(eligible_movies) == 0:
                return DoubleDip(movie)

            # otherwise, we recursively branch out and explore
            # all the potential paths
            all_dips_from_movie = []
            for eligible_movie in eligible_movies:

                double_dips = find_all_dips_starting_from(eligible_movie, pruned_showtimes)

                if isinstance(double_dips, DoubleDip):
                    double_dips.prepend(movie)
                    all_dips_from_movie.append(double_dips)
                else:
                    # double dips should be a list
                    for double_dip in double_dips:
                        double_dip.flat_prepend(movie)
                        all_dips_from_movie.append(double_dip)

            return all_dips_from_movie

        # sort showtimes in ASC start-time...
        self.showtimes.sort(key=attrgetter('start'))

        # create a running count of which movies have been visited to avoid
        # making redundant double dips
        visited_movies = set()

        self.double_dips = []

        for movie in self.showtimes:

            # if we've finally arrived at a movie that's been visited, then
            # we know that we don't have to bother calculating any dips for it,
            # since self.showtimes is sorted by time, and all the other movies that
            #  may PRECEED `movie` have already been visited, and thus, so has `movie`.
            if movie in visited_movies:
                continue

            # finding dips is a recursive procedure that needs to start with some
            # context; in particular, at the beginning of each procedure, we don't
            # want to start with a theatre's entire set of showtimes. We want to
            # start with a pruned set of showtimes that already excludes future showings
            # of the same title:
            pruned_showtimes = [x for x in self.showtimes if x.name != movie.name]
            # further more, we want this array to be carried forward and "perpetually
            # filtered" throughout recursive calls to find_all_dips_starting_from().


            # dips can either be a single DoubleDip object, or a [DoubleDips].
            # if the latter, we can just + dips to self.double_dips.
            # if the former, +'ing will cast the DoubleDip back down to a movie.
            # This is undesirable for printing purposes later (when we want
            # to convert to JSON).
            dips = find_all_dips_starting_from(movie, pruned_showtimes)

            # if movie is a terminal node, dips is just a DoubleDip singleton,
            # otherwise it's a list of DoubleDip objects
            if isinstance(dips, DoubleDip):
                self.double_dips.append(dips)
            else:
                self.double_dips += dips

        return (self.double_dips)
