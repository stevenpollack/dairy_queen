import pandas as pd
import datetime
import time
import itertools
import re

"""
a -> c -> b
|    \
e     d

V = [a, b, c, d, e]
V.pop -> [a]
a.neighbors -> [c]
-- for each neighbor of a ... --

c.neighbors -> [b, d]
b.neighbors -> []
return b
d.neighbors -> []
return d
pre-pend c to returns -> [[c,b], [c,d]]

e.neighbors -> []
return e

pre-pend a to returns [[a,c,b],[a,c,d]]

def f(v):
    if neighbors.empty:
    return v
    else:
    return [v.prepend(f(x)) for x in v.neighbors]


start at a node
gather neighbors in a stack
pop neighbor in visited

"""

def find_next_showings(movie, kino_program, max_waiting_mins, acceptable_overlap_mins=0):
    
    # I anticipate 'movie' to be a row from a DataFrame, so we should
    # unpack elements using `.` and `iloc`...
    movie_title = movie.title.iloc[0]
    movie_end_time = movie.movie_end_time.iloc[0]
    
    latest_start_time = movie_end_time + datetime.timedelta(minutes=max_waiting_mins)
    overlap_duration = datetime.timedelta(minutes=acceptable_overlap_mins)
        
    # filter out:
    # 1. all future showings of the 'movie_title'
    # 2. all movies that start outside of the acceptable waiting period
    # include:
    # 1. movies that start during or after overlap period
    row_filter = \
        (kino_program.title != movie_title) & \
        (kino_program.movie_start_time >= movie_end_time - overlap_duration) & \
        (kino_program.movie_start_time <= latest_start_time)
        
    return kino_program[row_filter]

def movie_to_string(movie):
    """ 
    output looks something like:
    
    Alles steht Kopf (OV) (14:20-15:55)
    
    movie_title + ( + start_time + - + end_time + )
    
    movie should be a row from DataFrame with columns
    'title', 'start_time', and 'end_time'
    """
    return movie.title.iloc[0] + " (" + \
    movie.start_time.iloc[0].strftime("%H:%M") + "-" + \
    movie.movie_end_time.iloc[0].strftime("%H:%M") + ")"
    
def double_dip(starting_show, showtimes, max_waiting_mins=45, acceptable_overlap_mins=0):
    # filter out all future showings of 'starting_show':
    # this has to be done on 'showtimes' before any recursion
    # so the filtration can propagate forwards
    showtimes = showtimes[showtimes.title != starting_show.title.iloc[0]]
    
    # determine the next closest 'cluster' of shows
    next_showtimes = find_next_showings(starting_show,showtimes, max_waiting_mins, acceptable_overlap_mins)
    
    starting_show_info = movie_to_string(starting_show)
    
    # if there are no future shows, we're at a leaf node;
    # so, we should just output the show info
    if next_showtimes.empty:
        return starting_show_info
    
    # otherwise, for every show identified from 'find_next_shows'
    # we should collect the returned double-dips, "paths"
    paths = []
    
    for row in xrange(next_showtimes.shape[0]):
        next_show = next_showtimes.iloc[[row]]
        valid_double_dips = double_dip(next_show, showtimes, max_waiting_mins, acceptable_overlap_mins)
        
        """
        valid_double_dips can have two outputs:
         
        1. base-case: which is just movie info
        2. recursive-case: a list of valid (formatted) double dips
        
        In 1., we need to format the output to the form
        
            movie1_info -> movie2_info
        
        In 2., we just need to pre-pend starting_show_info to the
        already formatted output.
        """ 
        if isinstance(valid_double_dips, basestring):
            paths.append(starting_show_info + " -> " + valid_double_dips)
        else:
            # if valid_double_dips is a list (of lists) flatten it back
            # down to a list of strings
            if isinstance(valid_double_dips[0], list):
                valid_double_dips = [x for x in itertools.chain.from_iterable(valid_double_dips)]
            
            # prepend info
            tmp = [starting_show_info + " -> " + double_dips for double_dips in valid_double_dips]
            [paths.append(x) for x in tmp]
    
    return paths

def find_all_double_dips(showtimes,
                         max_waiting_mins=45,
                         acceptable_overlap_mins=0,
                         movies_to_exclude=None,
                         interesting_movies=None,
                         all_interesting_movies_must_be_in_dip=True):
   
    if movies_to_exclude: # so it isn't None
        if not isinstance(movies_to_exclude, list):
            if not isinstance(movies_to_exclude, str):
                raise TypeError("'movies_to_exclude' needs to be a string or list of strings", movies_to_exclude)
                
            movies_to_exclude = [movies_to_exclude]
            # filter movies
        exclusion_regexp = re.compile('|'.join(movies_to_exclude))
        
    if movies_to_exclude:
        movie_filter = [False if exclusion_regexp.findall(title) else True for title in showtimes.title]
        showtimes = showtimes[movie_filter]
        
    if interesting_movies:
        if not isinstance(interesting_movies, list):
            if not isinstance(interesting_movies, str):
                raise TypeError("'interesting_movies' needs to be a string or list of strings", interesting_movies)
                
            interesting_movies = [interesting_movies]
            
    double_dips = []
    for row in xrange(showtimes.shape[0]):
        tmp = double_dip(showtimes.iloc[[row]], showtimes, max_waiting_mins, acceptable_overlap_mins)
        if isinstance(tmp, list):
            [double_dips.append(x) for x in tmp]
        else: 
            double_dips.append(tmp)
    
    if interesting_movies:
        if all_interesting_movies_must_be_in_dip:
            output = []
            for dip in double_dips:
                keep_dip = True
                for movie in interesting_movies:
                    if not re.findall(pattern=movie, string=dip):
                        keep_dip = False
                        break
                if keep_dip:
                    output.append(dip)
            return output
        else:     
            inclusion_regexp = re.compile('|'.join(interesting_movies))
            double_dips = [dip if inclusion_regexp.findall(dip) else None for dip in double_dips]
            double_dips = filter(None, double_dips)      
            return double_dips
    else:
        return double_dips

"""
Helper functions to create DataFrame input for double dip algorithm
"""
def initialize_movie_df(title, showtimes, runtime, ads_mins=0, trailers_mins=0):
    ads_timedelta = datetime.timedelta(minutes=ads_mins)
    trailers_timedelta = datetime.timedelta(minutes=trailers_mins)
    runtime_timedelta = datetime.timedelta(minutes=int(runtime))
    
    # if showtimes is a single string, list-comprehension will
    # move over the characters in the string, which is no-bueno.
    # Instead, wrap the string into a list
    if not isinstance(showtimes, list):
        showtimes = [showtimes]
    
    presentation_start_timedates = [datetime.datetime.strptime(showtime, '%H:%M') for showtime in showtimes]
    movie_start_timedates =  [start_time + ads_timedelta + trailers_timedelta for start_time in presentation_start_timedates]
    presentation_end_timedates = [movie_start_timedate + runtime_timedelta for movie_start_timedate in movie_start_timedates]
    output = pd.DataFrame({'start_time':presentation_start_timedates, \
                           'movie_start_time':movie_start_timedates,\
                           'movie_end_time':presentation_end_timedates})
    output['title'] = title
    return(output)

def make_showtimes(showtimes_api_results, ads_mins=0, trailers_mins=0):
    # cobble together "kino_program", a DataFrame which has the start and end times for all
    # movies being pulled down from showtimes API
    kino_program = pd.DataFrame()

    for movie in showtimes_api_results['results']['Movies']:
        kino_program = \
        kino_program.append(ignore_index=True,\
                            other=initialize_movie_df(movie['title'], movie['showtimes'], movie['runtime'], ads_mins, trailers_mins))

    return kino_program