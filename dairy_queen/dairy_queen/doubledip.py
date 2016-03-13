import collections
from .movie import Movie

# SO- flatten arbirtrary list:
# http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python#2158532
# this yields a GENERATOR, not a list...
def flatten_list(self):
    for el in self:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes, dict)):
            for sub in flatten_list(el):
                yield sub
        else:
            yield el

class FlatList(list):
    """
    This list is basically a semi-self-flattening list.

    It flattens iterables upon initialization and supports
    the ability to compose append/preprend and flatten.

    Both the append and prepend methods return the modified object
    which allow for .-chaining
    """

    def __init__(self, iterable = None):
        self.append(iterable)
        self.flatten()

    def flatten(self):
        flattened_list = flatten_list(self.copy())
        self.clear()
        for x in flattened_list:
            self.append(x)
        return(self)

    def append(self, p_object):
        super().append(p_object)
        return(self)

    def prepend(self, x):
        self.insert(0, x)
        return(self)

    def flat_prepend(self, x):
        return(self.prepend(x).flatten())

    def flat_append(self, x):
        return(self.append(x).flatten())

class DoubleDip(FlatList):
    def __init__(self, movies):
        throw_error = False
        if isinstance(movies, Movie):
            self.append(movies)
        elif isinstance(movies, list):
            for movie in movies:
                if not isinstance(movie, Movie):
                    throw_error = True
                    break
                self.append(movie)

        if throw_error:
            raise TypeError("DoubleDip can only be initialized from a movie or list of movies.")

    def to_json(self, showtime_format='%H:%M'):
        self.json = [movie.to_json(showtime_format) for movie in self]
        return self.json

    def __repr__(self):
        output = "DoubleDip([" + ", ".join([movie.__repr__() for movie in self]) + "])"
        return(output)

    def __str__(self):
        output = "Double Dip connecting:\n" + "\n".join([movie.__str__() for movie in self])
        print(output)