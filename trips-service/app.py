from flask_socketio import SocketIO, send, emit
from flask import Flask, request
from flask_cors import CORS
import json
import copy
import random
import appconfig

app = Flask(__name__)
CORS(app)
app.config.from_object('appconfig.Config')


socketio = SocketIO(app, cors_allowed_origins='*')

active_navigations = {}
trips = []

class Trip:
    def __init__(self, trip_id, feature_geoJson):
        self.id = trip_id
        self.feature_geoJson = feature_geoJson
        self.name = feature_geoJson['properties']['name']
        self.coordinates = feature_geoJson['geometry']['coordinates'][0]

    def get_start_navigation(self):
        # Start navigation with starting point only
        feature_geoJson = copy.deepcopy(self.feature_geoJson)
        feature_geoJson['geometry']['coordinates'][0] = [ feature_geoJson['geometry']['coordinates'][0][0] ]

        geoJson = {
            "type": "FeatureCollection",
            "features": [ feature_geoJson ]
        }

        navigation_start = { "tripId": self.id, "geoJson": geoJson }

        return navigation_start



def add_navigation(sid, trip_id, position=0):
    print(f"Adding client {sid} to active navigations")
    active_navigations[sid] = { "trip_id": trip_id, "position": position }

def remove_navigation(sid):
    if sid in active_navigations:
        print(f"Removing client {sid} from active navigations")
        del active_navigations[sid]

def load_trips():
    global trips
    with open('trip.geoJson') as json_file:
        data = json.load(json_file)
        trip_id = 0

        for trip_geoJson in data['features']:
            trip = Trip(trip_id, trip_geoJson)
            trips.append(trip)
            trip_id += 1
    
    print(f'Loaded {len(trips)} trips')


@app.route('/healthcheck')
def healthcheck():
    return { "status": "up"}


@app.route('/trips')
def get_trips():
    trips_summary =  [{ "tripId": trip.id, "tripName": trip.name } for trip in trips]
    return {
        "trips": trips_summary
    }



@socketio.on('connect')
def connect_web():
    print('[INFO] Web client connected', request.sid, "on", request.namespace)


@socketio.on('disconnect')
def disconnect_web():
    print('[INFO] Web client disconnected', request.sid, "from", request.namespace)
    remove_navigation(request.sid)

@socketio.on('startNavigation')
def start_navigation(data):
    print(request.sid, '[INFO] Received startNavigation: ', data)

    if data.get('tripId', None) is None:
        # Live navigation simulation, pick a random trip
        trip_id = random.randint(0, len(trips) - 1)
    else:
        # Use an specific trip for navigation
        trip_id = int(data.get('tripId'))

    navigation_init_data = trips[trip_id].get_start_navigation()
    emit('navigationInit', navigation_init_data)

    add_navigation(request.sid, trip_id=trip_id)



@socketio.on('resumeNavigation')
def resume_navigation(data):
    print(request.sid, '[INFO] Received resumeNavigation: ', data)
    add_navigation(request.sid, trip_id=data['tripId'], position=data['lastPositionIndex'])


def simulation_delay():
    min = app.config["SIMULATION_DELAY_SECONDS_MINIMUM"]
    max = app.config["SIMULATION_DELAY_SECONDS_MAXIMUM"]

    delay = random.uniform(min, max)

    socketio.sleep(delay)




def simulate_location_updates():
    print("Started simulation thread")
    while True:
        simulation_delay()
        print("Simulating updates for navigation clients")

        # Send updates to active navigations
        for sid, navigation in active_navigations.items():
            trip_id = navigation['trip_id']
            trip = trips[trip_id]

            positions = trip.coordinates
            next_position = navigation['position'] + 1

            if next_position >= len(positions):
                # We shouldn't normally get here if navigation has ended, it will be handled later
                navigation['finished'] = True
                continue

            socketio.emit('positionUpdates', { "positions": [ positions[next_position] ]}, room=sid)

            navigation['position'] = next_position

            # Check if we finished navigation
            if next_position == len(positions) - 1:
                navigation['finished'] = True

        # Stop tracking any navigations that have finished
        finished_sids = [sid for sid in active_navigations if active_navigations[sid].get('finished', False)]
        for sid in finished_sids:
            remove_navigation(sid)


if __name__ == "__main__":
    load_trips()
    print('[INFO] Starting server at http://localhost:5001')
    socketio.start_background_task(simulate_location_updates)
    # Background tasks do not work with reloader https://github.com/miguelgrinberg/Flask-SocketIO/issues/617
    socketio.run(app=app, host='0.0.0.0', port=5001, use_reloader=False, debug=True)
