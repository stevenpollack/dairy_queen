from dairy_queen.doubledip import DoubleDip
from dairy_queen.movie import Movie

class TestDoubleDip:
    def test_to_json(self):

        doubledip = DoubleDip([
            Movie(name='a', runtime=60, showtime='12:45'),
            Movie(name='b', runtime=120, showtime='14:00')
        ])

        json_output = [
            {
                'movie': 'a',
                'length': 60,
                'startTime': '12:45',
                'endTime': '13:45'
            },
            {
                'movie': 'b',
                'length': 120,
                'startTime': '14:00',
                'endTime': '16:00'
            }
        ]

        assert doubledip.to_json() == json_output