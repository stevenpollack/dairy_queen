import requests
from bs4 import BeautifulSoup
import re
import warnings # https://docs.python.org/3.5/library/exceptions.html

def extract_theatres_and_showtimes(parsed_req):
    
    #~~~~~~~~~~~~~~~~~~
    # helper functions
    #~~~~~~~~~~~~~~~~~~
    def runtime_to_minutes(runtime):  
        hours = 0
        minutes = 0
        warning_thrown = False

        hours_match = re.search('\d(?=hr|:)', runtime)
        minutes_match = re.search('(\d{1,2}(?=min))', runtime)

        if hours_match:
            hours = int(hours_match.group())
        else:
            warnings.warn("Couldn't extract hours from " + movie_name + "'s runtime (" + runtime + ")")
            warning_thrown = True

        if minutes_match:
            minutes = int(minutes_match.group())
        else:
            warnings.warn("Couldn't extract minutes from " + movie_name + "'s runtime (" + runtime + ")")
            warning_thrown = True

        return(hours*60 + minutes, warning_thrown)
    
    def extract_theatre_properties(description):
        theatre_name_a = description.select('.name a')[0]

        theatre_name, theatre_href, theatre_id, warning_thrown = extract_name_id_and_url(theatre_name_a, 'theatre')

        theatre_info = description.select('.info')[0].get_text().split(" - ")
        theatre_address = theatre_info[0]
        theatre_phone_number = None

        if (len(theatre_info) == 2):
            theatre_phone_number = theatre_info[1]
        elif (len(theatre_info) > 2):
            warnings.warn("'theatre_info' has more entries than expected: " + ", ".join(theatre_info))

        theatre_dict = {
            'name': theatre_name,
            'address': theatre_address,
            'phone_number': theatre_phone_number,
            'tid': theatre_id,
            'url': theatre_href,
            'program': [],
            'warning_thrown': warning_thrown
        }

        return(theatre_dict)
    
    def extract_name_id_and_url(name_a, id_type):
        if (id_type == 'theatre'):
            id_type = 'tid'
        elif (id_type == 'movie'):
            id_type = 'mid'
        else:
            raise ValueError("'id_type' can either be 'theatre' or 'movie'.")  

        warning_thrown = False

        href = name_a.attrs['href']

        id_match = re.search("(?<=" + id_type + "=)(\w*)", href)
        if (id_match):
            google_id = id_match.group()
        else:
            google_id = None
            warnings.warn("Couldn't extract " + id_type + " from " + href)
            warning_thrown = True

        name = name_a.get_text()

        return(name, href, google_id, warning_thrown)
    
    #~~~~~~~~~~~~~~~~~~
    # function body
    #~~~~~~~~~~~~~~~~~~
    theatres = []
    for theatre in parsed_req.body.select('.theater'):

        # extract theatre-level information (name, address, url, etc.)
        description = theatre.select('.desc')

        if (len(description) != 1):
            raise AssertionError("theatre's 'description' has " + str(len(description)) + " entries -- expected 1.")

        theatre_dict = extract_theatre_properties(description[0])    

        # build the theatre program: an array of dictionaries, each dictionary
        # corresponds to a particular movie
        theatre_program = []
        for movie in theatre.select('.showtimes .movie'):
            movie_name_a = movie.select('.name a')[0]

            movie_name, movie_href, movie_id, warning_thrown = extract_name_id_and_url(movie_name_a, 'movie')

            movie_info = movie.select('.info')[0].get_text().split(' - ')
            movie_runtime = movie_info[0]
            movie_rating = None 
            misc_info = None

            if (len(movie_info) >= 2):
                movie_rating = movie_info[1]

                if (len(movie_info) > 2):
                    misc_info = " - ".join(movie_info[2:])
                    #warnings.warn(movie_name + "'s 'movie_info' has more entries than expected: " + ", ".join(movie_info))
                    #warning_thrown = True

            movie_showtimes = []
            for showtime_span in movie.select('.times span[style^="color"]'):
                # extract only the time (in case there are some weird characters)
                extracted_showtime = showtime_span.get_text()
                showtime_match = re.search('\d{1,2}:\d{2}', extracted_showtime)
                if showtime_match:
                    movie_showtimes.append(showtime_match.group())
                else:
                    warnings.warn("Couldn't extract showtime from input " + extracted_showtime)
                    warning_thrown = True

            movie_runtime, runtime_conversion_warning = runtime_to_minutes(movie_runtime)

            if (runtime_conversion_warning):
                warning_thrown = True

            theatre_program.append(
                {
                    'name': movie_name,
                    'url': movie_href,
                    'mid': movie_id,
                    'showtimes': movie_showtimes,
                    'runtime': movie_runtime,
                    'rating': movie_rating,
                    'misc_info': misc_info,
                    'warning_thrown': warning_thrown
                }
            )

        theatre_dict['program'] = theatre_program
        theatres.append(theatre_dict)
        
    return(theatres)

def extract_next_page_url(parsed_req):
    next_url = None
    for td_a in parsed_req.body.select('td a'):
        if re.search('Next', td_a.get_text()):
            next_url = 'http://google.com' + td_a.attrs['href']
            break
    return(next_url)

def extract_all_theatres_and_showtimes(near, days_from_now):
    
    # check that near is a string
    if not isinstance(near, str):
        raise TypeError("'near' must be a string.")
        
    # cast days_from_now as integer
    days_from_now = int(days_from_now)
    
    starting_url = "http://www.google.com/movies"
    get_params = {
        'near': near,
        'date': days_from_now
    }
    
    parsed_req = BeautifulSoup(requests.get(starting_url, get_params).text, 'html.parser')
    
    theatres_and_showtimes = extract_theatres_and_showtimes(parsed_req)
    next_page_url = extract_next_page_url(parsed_req)
    
    while (next_page_url is not None):
        parsed_req = BeautifulSoup(requests.get(next_page).text, 'html.parser')
        next_page_url = extract_next_page_url(parsed_req)
        theatres_and_showtimes += extract_theatres_and_showtimes(parsed_req)
    
    return(theatres_and_showtimes)