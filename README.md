This project implements a car tracking application consiting of two parts, trips-ui which is the front end of the application and trips-service for the backend.

Start trips-service by reading it's [README](trips-service/README.md)
Start trips-ui by performing `ng serve --open` and then open http://localhost:4200/ in your browser

Features:
- Live tracking picks one of the three available trips in the backend and pretends to be live tracking an inprogress trip.
- History lists the three available trips, which you can select to replay.
- If `trips-service` is stopped and restarted during tracking/replay then tracking will resume from where it disconnected.
- During tracking/replay you have the option to select a previous position to focus on it. Updates will continue to come in but you will need to select follow for the view to follow the car.

Have fun!