from flask_socketio import SocketIO, send, emit
from flask import Flask, request
import json
import copy

app = Flask(__name__)
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



def add_navigation(sid, trip_id):
    print(f"Adding client {sid} to active navigations")
    active_navigations[sid] = { "trip_id": trip_id, "position": 0 }

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


@socketio.on('connect')
def connect_web():
    print('[INFO] Web client connected', request.sid, "on", request.namespace)


@socketio.on('disconnect')
def disconnect_web():
    # TODO remove if disconnected
    print('[INFO] Web client disconnected', request.sid, "from", request.namespace)

@socketio.on('startNavigation')
def startNavigation(data):
    print(request.sid, '[INFO] Received startNavigation: ', data)

    navigation_init_data = trips[0].get_start_navigation()

    emit('navigationInit', navigation_init_data)
    # TODO random pick on trip_id
    add_navigation(request.sid, trip_id=0)




def simulate_location_updates():
    # TODO load from a file
    positions = trips[0].coordinates

    print("Started simulation thread")
    while True:
        # TODO make time configurable and random in a range
        socketio.sleep(1)

        print("Simulating updates for navigation clients")

        # Send updates to active navigations
        for sid, navigation in active_navigations.items():
            trip_id = navigation['trip']
            positions = 
            next_position = navigation['position'] + 1
            # TODO Check on positions based on journey
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
    # TODO Background tasks do not work with reloader https://github.com/miguelgrinberg/Flask-SocketIO/issues/617
    socketio.run(app=app, host='0.0.0.0', port=5001, use_reloader=False, debug=True)
