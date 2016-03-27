import pytest, json  # for fixtures
from dairy_queen.theatre import Theatre
from dairy_queen.doubledip import DoubleDip
from operator import attrgetter  # this is for sorting


# only import test json once per session.
@pytest.fixture(scope='module')
def theatre_json():
    return json.load(open('dairy_queen/tests/example_theatre.json'))

def create_theatre_and_calc_double_dips(theatre_json, max_waiting_mins=20, max_overlap_mins=6):
    theatre = Theatre(name=theatre_json['name'], showtimes=theatre_json['showtimes'])
    theatre.calculate_double_dips(max_waiting_mins, max_overlap_mins)
    theatre.showtimes.sort(key=attrgetter('name'))
    return theatre

@pytest.fixture(scope='module')
def prototypical_showtimes():
    return json.load(open('dairy_queen/tests/prototypical_showtimes.json'))


class TestTheatre:
    def test_calculate_double_dip_1(self, theatre_json):
        # we should expect to see a list of 1 double dip, connecting
        # movie 'a' to movie 'b'
        theatre = create_theatre_and_calc_double_dips(theatre_json[0])

        expected_dips = [
            DoubleDip([theatre.showtimes[0], theatre.showtimes[1]])
        ]

        assert theatre.double_dips == expected_dips

    def test_calculate_double_dip_2(self, theatre_json):
        # we should expect to see a list of 1 double dip,
        # connecting movie 'a' to 'b'
        theatre = create_theatre_and_calc_double_dips(theatre_json[1])

        expected_dips = [
            DoubleDip([theatre.showtimes[0], theatre.showtimes[1]])
        ]

        assert theatre.double_dips == expected_dips

    def test_calculate_double_dip_3(self, theatre_json):
        # we should expect to see a list of 2 dips,
        # since the distance between start times is too wide
        theatre = create_theatre_and_calc_double_dips(theatre_json[2])

        expected_dips = [
            DoubleDip(theatre.showtimes[0]),
            DoubleDip(theatre.showtimes[1])
        ]

        assert theatre.double_dips == expected_dips

    def test_calculate_double_dip_4(self, theatre_json):
        # we should expect to see a list of 2 dips,
        # since the overlap between movies is too great
        theatre = create_theatre_and_calc_double_dips(theatre_json[3])

        expected_dips = [
            DoubleDip(theatre.showtimes[0]),
            DoubleDip(theatre.showtimes[1])
        ]

        assert theatre.double_dips == expected_dips

    def test_calculate_double_dip_5(self, theatre_json):
        # we should expect to see a list of 2 dips, one is a
        # double, the other is a single, since the last film
        # is too far away from the first two...
        theatre = create_theatre_and_calc_double_dips(theatre_json[4])

        expected_dips = [
            DoubleDip([theatre.showtimes[0], theatre.showtimes[1]]),
            DoubleDip(theatre.showtimes[2])
        ]

        assert theatre.double_dips == expected_dips

    def test_calculate_double_dip_6(self, theatre_json):
        # we should expect to see a list of 1 dip, which
        # connects all movies.
        theatre = create_theatre_and_calc_double_dips(theatre_json[5])

        expected_dips = [
            DoubleDip([theatre.showtimes[0],
                       theatre.showtimes[1],
                       theatre.showtimes[2]])
        ]

        assert theatre.double_dips == expected_dips

    def test_to_json(self):
        theatre_json = {
            "name": "Test Theatre 5",
            "description": "Test triplet when there's an unacceptable distance",
            "showtimes": [
                {
                    "name": "a",
                    "runtime": 60,
                    "times": ["16:00"]
                },
                {
                    "name": "b",
                    "runtime": 60,
                    "times": ["17:05"]
                },
                {
                    "name": "c",
                    "runtime": 60,
                    "times": ["19:05"]
                }
            ]
        }

        expected_output = {
            'name': theatre_json['name'],
            'info': theatre_json.get('info'),
            'doubleDips': [
                [
                    {
                        'movie': theatre_json['showtimes'][0]['name'],
                        'length': theatre_json['showtimes'][0]['runtime'],
                        'startTime': theatre_json['showtimes'][0]['times'][0],
                        'endTime': "17:00"
                    },
                    {
                        'movie': theatre_json['showtimes'][1]['name'],
                        'length': theatre_json['showtimes'][1]['runtime'],
                        'startTime': theatre_json['showtimes'][1]['times'][0],
                        'endTime': "18:05"
                    }
                ],
                [
                    {
                        'movie': theatre_json['showtimes'][2]['name'],
                        'length': theatre_json['showtimes'][2]['runtime'],
                        'startTime': theatre_json['showtimes'][2]['times'][0],
                        'endTime': "20:05"
                    }
                ]
            ]
        }

        theatre = Theatre(name=theatre_json.get('name'),
                          showtimes=theatre_json.get('showtimes'),
                          info=theatre_json.get('info'))

        assert theatre.to_json() == expected_output

    def test_case_1(self, prototypical_showtimes):
        theatre = Theatre(name=prototypical_showtimes[0]['name'], showtimes=prototypical_showtimes[0]['showtimes'])
        theatre.calculate_double_dips(max_waiting_time=0, max_overlap_time=0)

        expected_dips = [DoubleDip(theatre.showtimes[0]), DoubleDip(theatre.showtimes[1])]

        assert theatre.double_dips == expected_dips

    def test_case_2(self, prototypical_showtimes):
        theatre = create_theatre_and_calc_double_dips(prototypical_showtimes[1], max_waiting_mins=60,
                                                      max_overlap_mins=0)

        expected_dips = [
            DoubleDip(theatre.showtimes[0]),
            DoubleDip([theatre.showtimes[2], theatre.showtimes[1]])
        ]

        assert theatre.double_dips == expected_dips

    def test_case_3(self, prototypical_showtimes):
        theatre = create_theatre_and_calc_double_dips(prototypical_showtimes[2],
                                                      max_waiting_mins=60,
                                                      max_overlap_mins=0)

        expected_dips = [
            DoubleDip([theatre.showtimes[0], theatre.showtimes[3]]),
            DoubleDip([theatre.showtimes[2], theatre.showtimes[1]])
        ]

        assert theatre.double_dips == expected_dips

    def test_case_4(self, prototypical_showtimes):
        theatre = create_theatre_and_calc_double_dips(prototypical_showtimes[3],
                                                      max_waiting_mins=60,
                                                      max_overlap_mins=0)

        expected_dips = [
            DoubleDip([theatre.showtimes[0], theatre.showtimes[4]]),
            DoubleDip([theatre.showtimes[3], theatre.showtimes[1]]),
            DoubleDip(theatre.showtimes[2])
        ]

        assert theatre.double_dips == expected_dips

    def test_case_5(self, prototypical_showtimes):
        theatre = create_theatre_and_calc_double_dips(prototypical_showtimes[4],
                                                      max_waiting_mins=60,
                                                      max_overlap_mins=0)
        expected_dips = [
            DoubleDip([theatre.showtimes[0], theatre.showtimes[3]]),
            DoubleDip([theatre.showtimes[0], theatre.showtimes[4]]),
            DoubleDip([theatre.showtimes[2], theatre.showtimes[1]]),
            DoubleDip([theatre.showtimes[2], theatre.showtimes[4]]),
        ]

        assert theatre.double_dips == expected_dips

    def test_case_6(self, prototypical_showtimes):
        theatre = create_theatre_and_calc_double_dips(prototypical_showtimes[5],
                                                      max_waiting_mins=60,
                                                      max_overlap_mins=0)

        expected_dips = [
            DoubleDip([theatre.showtimes[0], theatre.showtimes[4], theatre.showtimes[8]]),
            DoubleDip([theatre.showtimes[0], theatre.showtimes[7], theatre.showtimes[5]]),
            DoubleDip([theatre.showtimes[3], theatre.showtimes[1], theatre.showtimes[8]]),
            DoubleDip([theatre.showtimes[3], theatre.showtimes[7], theatre.showtimes[2]]),
            DoubleDip([theatre.showtimes[6], theatre.showtimes[1], theatre.showtimes[5]]),
            DoubleDip([theatre.showtimes[6], theatre.showtimes[4], theatre.showtimes[2]])
        ]

        assert theatre.double_dips == expected_dips


def cinestar_berlin(self):
    cinestar_berlin = json.load(open('dairy_queen/tests/cinestar_berlin.json'))
    theatre = Theatre(name=cinestar_berlin['name'], showtimes=cinestar_berlin['showtimes'])

    # test the situation where all films should be singleton dips:
    # setting max_waiting_time=0 & max_overlap_time=-5 is an impossible condition
    theatre.calculate_double_dips(max_waiting_time=0, max_overlap_time=-5)
    expected_dips = [
        DoubleDip(movie) for movie in theatre.showtimes
        ]
    assert theatre.double_dips == expected_dips

    # test the situation where only films that are perfectly back-to-back are
    # double dips
    theatre.calculate_double_dips(max_waiting_time=0, max_overlap_time=0)
    non_trivial_dips = []
    for double_dip in theatre.double_dips:
        if len(double_dip) > 1:
            non_trivial_dips.append(double_dip)
    expected_dips = []

    assert non_trivial_dips == expected_dips
