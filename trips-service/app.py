from flask_socketio import SocketIO, send, emit
from flask import Flask, render_template

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/healthcheck')
def healthcheck():
    return { "status": "up"}


@socketio.on('connect')
def connect_web():
    print('[INFO] Web client connected')

@socketio.on('disconnect')
def disconnect_web():
    print('[INFO] Web client disconnected')

@socketio.on('json')
def on_json(json):
    print('[INFO] Received json: ', json)


@socketio.on('message')
def on_message(data):
    print('[INFO] Received message: ', data)

@socketio.on('startNavigation')
def startNavigation(data):
    print('[INFO] Received startNavigation: ', data)

    navigation_init_data = { 
        "journeyId": 0,
        "geoJson": {
            "type": "FeatureCollection",
            "features": [
            {
                "type": "Feature",
                "properties": {
                "name": "Ayiou Athanasiou 28, Agios Athanasios 4102, Cyprus to Arrivals 5, Larnaca, Cyprus"
                },
                "geometry": {
                "type": "MultiLineString",
                "coordinates": [
                    [
                    [
                        33.05986,
                        34.70234
                    ]
                    ]
                ]
                }
            }
            ]
        }
    }

    emit('navigationInit', navigation_init_data)




def simulate_location_updates():
    print("Started simulation thread")
    while True:
        # TODO make time configurable and random in a range
        socketio.sleep(1)
        #print("Simulating updates for navigation clients")


if __name__ == "__main__":
    print('[INFO] Starting server at http://localhost:5001')
    socketio.start_background_task(simulate_location_updates)
    # TODO Background tasks do not work with reloader https://github.com/miguelgrinberg/Flask-SocketIO/issues/617
    socketio.run(app=app, host='0.0.0.0', port=5001, use_reloader=False, debug=True)
