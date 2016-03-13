import pytest  # for fixtures
from dairy_queen.theatre import Theatre
from dairy_queen.doubledip import DoubleDip
from operator import attrgetter  # this is for sorting


# only import test json once per session.
@pytest.fixture(scope = 'module')
def theatre_json():
    import json
    return json.load(open('dairy_queen/tests/example_theatre.json'))

def create_theatre_and_calc_double_dips(theatre_json, max_waiting_mins = 20, max_overlap_mins = 6):
    theatre = Theatre(name = theatre_json['name'], program = theatre_json['program'])
    theatre.calculate_double_dips(max_waiting_mins, max_waiting_mins)
    theatre.program.sort(key = attrgetter('name'))
    return (theatre)

class TestTheatre:

    def test_calculate_double_dip_1(self, theatre_json):
        # we should expect to see a list of 1 double dip, connecting
        # movie 'a' to movie 'b'
        theatre = create_theatre_and_calc_double_dips(theatre_json[0])

        expected_dips = [
            DoubleDip([theatre.program[0], theatre.program[1]])
        ]

        assert theatre.double_dips == expected_dips

    def test_calculate_double_dip_2(self, theatre_json):
        # we should expect to see a list of 1 double dip,
        # connecting movie 'a' to 'b'
        theatre = create_theatre_and_calc_double_dips(theatre_json[1])

        expected_dips = [
            DoubleDip([theatre.program[0], theatre.program[1]])
        ]

        assert theatre.double_dips == expected_dips

    def test_calculate_double_dip_3(self, theatre_json):
        # we should expect to see a list of 2 dips,
        # since the distance between start times is too wide
        theatre = create_theatre_and_calc_double_dips(theatre_json[2])

        expected_dips = [
            DoubleDip(theatre.program[0]),
            DoubleDip(theatre.program[1])
        ]

        assert theatre.double_dips == expected_dips

    def test_calculate_double_dip_4(self, theatre_json):
        # we should expect to see a list of 2 dips,
        # since the overlap between movies is too great
        theatre = create_theatre_and_calc_double_dips(theatre_json[3])

        expected_dips = [
            DoubleDip(theatre.program[0]),
            DoubleDip(theatre.program[1])
        ]

        assert theatre.double_dips == expected_dips

    def test_calculate_double_dip_5(self, theatre_json):
        # we should expect to see a list of 2 dips, one is a
        # double, the other is a single, since the last film
        # is too far away from the first two...
        theatre = create_theatre_and_calc_double_dips(theatre_json[4])

        expected_dips = [
            DoubleDip([theatre.program[0], theatre.program[1]]),
            DoubleDip(theatre.program[2])
        ]

        assert theatre.double_dips == expected_dips

    def test_calculate_double_dip_6(self, theatre_json):
        # we should expect to see a list of 1 dip, which
        # connects all movies.
        theatre = create_theatre_and_calc_double_dips(theatre_json[5])

        expected_dips = [
            DoubleDip([theatre.program[0],
                       theatre.program[1],
                       theatre.program[2]])
        ]

        assert theatre.double_dips == expected_dips

    def test_to_json(self):
        theatre_json = {
            "name": "Test Theatre 5",
            "description": "Test triplet when there's an unacceptable distance",
            "program": [
                {
                    "name": "a",
                    "runtime": 60,
                    "showtimes": "16:00"
                },
                {
                    "name": "b",
                    "runtime": 60,
                    "showtimes": "17:05"
                },
                {
                    "name": "c",
                    "runtime": 60,
                    "showtimes": "19:05"
                }
            ]
        }

        expected_output = {
            'name': theatre_json['name'],
            'address': theatre_json.get('address'),
            'doubleDips': [
                [
                    {
                        'movie': theatre_json['program'][0]['name'],
                        'length': theatre_json['program'][0]['runtime'],
                        'startTime': theatre_json['program'][0]['showtimes'],
                        'endTime': "17:00"
                    },
                    {
                        'movie': theatre_json['program'][1]['name'],
                        'length': theatre_json['program'][1]['runtime'],
                        'startTime': theatre_json['program'][1]['showtimes'],
                        'endTime': "18:05"
                    }
                ],
                [
                    {
                        'movie': theatre_json['program'][2]['name'],
                        'length': theatre_json['program'][2]['runtime'],
                        'startTime': theatre_json['program'][2]['showtimes'],
                        'endTime': "20:05"
                    }
                ]
            ]
        }

        theatre = Theatre(name=theatre_json.get('name'),
                          program=theatre_json.get('program'),
                          address=theatre_json.get('address'))

        assert theatre.to_json() == expected_output