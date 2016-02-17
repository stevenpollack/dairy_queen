import pytest  # for fixtures
from theatre import Theatre
from doubledip import DoubleDip
from operator import attrgetter  # this is for sorting


# only import test json once per session.
@pytest.fixture(scope = 'module')
def theatre_json():
    import json
    return json.load(open('tests/example_theatre.json'))


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
