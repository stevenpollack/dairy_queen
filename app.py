from flask import Flask, request, json, Response, redirect
from requests import HTTPError
from warnings import warn
from iron_cache import IronCache
from dairy_queen.theatre import Theatre
import requests
from json import loads, dumps

#double_dip_cache = IronCache(name='double_dips')

app = Flask(__name__)
@app.route('/')
def route_to_apiary():
    apiary_io = 'http://docs.dairyqueen1.apiary.io/'
    return (redirect(apiary_io, code=302))

def hello_world():
    try:
        cache_key = create_cache_key(near, days_from_now)
        double_dips = json.loads(double_dip_cache.get(key=cache_key).value)
        warn('Fetched results from cache with key: ' + cache_key)
    except ValueError as ve:
        warn(str(ve))
        showtimes = json.dumps({'error': '`date` must be a base-10 integer'})
        status = 400
    except HTTPError as e:
        warn(str(e))
    return('hello world')

@app.route('/double-dips', methods=['GET'])
def get_doubledips():
    location = request.args.get('location')
    days_from_now = request.args.get('days_from_now')
    max_waiting_time = request.args.get('max_wait_mins')
    max_overlap_time = request.args.get('max_overlap_mins')

    status = None
    msg = None
    mimetype = 'application/json'

    if location is None or not isinstance(location, str):
        status = 400
        msg = "'location' is mandatory and must be a string."
        resp = Response(dumps({'msg': msg}), status=status, mimetype=mimetype)
        return resp

    if days_from_now is not None:
        try:
            days_from_now = int(days_from_now)
        except Exception:
            status = 400
            msg = "'days_from_now' must be a base-10 integer."
            resp = Response(dumps({'msg': msg}), status=status, mimetype=mimetype)
            return resp
    else:
        days_from_now = 0

    if max_waiting_time is not None:
        try:
            max_waiting_time = int(max_waiting_time)
        except Exception:
            status = 400
            msg = "'max_waiting_time' must be a base-10 integer"
            resp = Response(dumps({'msg': msg}), status=status, mimetype=mimetype)
            return resp
    else:
        max_waiting_time = 45

    if max_overlap_time is not None:
        try:
            max_overlap_time = int(max_overlap_time)
        except Exception:
            status = 400
            msg = "'max_overlap_time' must be a base-10 integer"
            resp = Response(dumps({'msg': msg}), status=status, mimetype=mimetype)
            return resp
    else:
        max_overlap_time = 5


    gms_url = 'http://google-movies-scraper.herokuapp.com/movies'
    gms_params = {
        'near': location,
        'date': days_from_now
    }

    # should definitely build some logic to handle response code of r...
    r = requests.get(gms_url, params=gms_params)
    theatres_json = loads(r.text)
    output = []
    for theatre in theatres_json:
        try:
            tmp_theatre = Theatre(name=theatre.get('name'),
                                  program=theatre.get('program'),
                                  address=theatre.get('address'))

            tmp_json = tmp_theatre.to_json(max_waiting_time=max_waiting_time,
                                           max_overlap_time=max_overlap_time)

            output.append(tmp_json)
        except TypeError as e:
            warn(str(e))

    status = 200
    resp = Response(dumps(output), status=status, mimetype=mimetype)
    return(resp)


if (__name__ == '__main__'):
    app.run(debug=True, host='0.0.0.0', port=5000)