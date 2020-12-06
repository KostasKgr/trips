import { Component, OnInit, ɵCompiler_compileModuleSync__POST_R3__ } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import * as mapboxgl from 'mapbox-gl';
import io from 'socket.io-client';

@Component({
  selector: 'app-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.css']
})
export class MapComponent implements OnInit {

  map: mapboxgl.Map;
  data = null;
  routeCoordinates = [];
  moveOnLiveUpdates = true;
  currentPosition = null;
  socket = null;
  tripId = null;

  // TODO race condition between map loading and socket connecting and getting more data
  // TODO if you click live after you have gone to a past trip, the navigation does not start over
  constructor(private route: ActivatedRoute) {

    this.route.queryParams.subscribe(params => {
      console.log("Params", params)
      this.tripId = 'tripId' in params ? params['tripId'] : null;
      console.log("Trip id", this.tripId)
  });


  }

  focus(coordinates) {
    // User focuses on a past position, we disable moving to new positions
    // so that he can inspect what he wanted
    this.moveOnLiveUpdates = false;
    console.log("Focusing on", coordinates);
    this.map.flyTo({
        center: coordinates,
        speed: 0.5
    });
  }

  resumeNavigation() {
    this.moveOnLiveUpdates = true;

    this.map.flyTo({
      center: this.currentPosition,
      speed: 0.5
    });    
  }

  fly(coordinates) {
    this.currentPosition = coordinates

    this.map.getSource('point').setData({
      'type': 'Point',
      'coordinates': this.currentPosition
    });

    if (!this.moveOnLiveUpdates) {
      return;
    }    

    this.map.flyTo({
        center: this.currentPosition,
        speed: 0.5
    });

  }

  onConnection(socket): void {
    console.log("Connected", this.socket)
    this.socket.emit('startNavigation', {tripId: this.tripId});

    // TODO continue navigation
    // this.socket.emit('continueNavigation', {tripId: ... , lastPositionIndex: ...});
  }

  onPositionUpdates(data): void {
    const newPositions = data.positions;
    this.routeCoordinates.push(...newPositions);

    console.log("New positions received:", data);

    this.map.getSource('route').setData(this.data);

    this.fly(this.routeCoordinates[this.routeCoordinates.length - 1]);
  }

  onNavigationInit(data): void {
    console.log("Initializing navigation", data)

    // TODO add loader while the connection is established in the beginning

    this.data = data.geoJson;
    this.routeCoordinates = this.data.features[0].geometry.coordinates[0];
    this.tripId = data.tripId;
    
    var startingPosition = this.routeCoordinates[this.routeCoordinates.length - 1];
    mapboxgl.accessToken = 'pk.eyJ1Ijoia29zdGFza2dyIiwiYSI6ImNraWF1bGw1bjBzeDcyc2xidmJ5NHA5NDkifQ.txJo3lqZ7Pw8jHVfZUTN2g'
    this.map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/streets-v11',
      zoom: 15,
      center: startingPosition
    });


    this.map.addControl(new mapboxgl.NavigationControl());

    


    this.map.on('load', () => {

      // https://docs.mapbox.com/mapbox-gl-js/example/geojson-line/
      this.map.addSource('route', {
        'type': 'geojson',
        'data': this.data
      });

      this.map.addLayer({
        'id': 'route',
        'type': 'line',
        'source': 'route',
        'layout': {
          'line-join': 'round',
          'line-cap': 'round'
        },
        'paint': {
          'line-color': '#0c8ced',
          'line-width': 4
        }
      });


      this.map.addSource('point', {
        'type': 'geojson',
        'data': {
          'type': 'Point',
          'coordinates': startingPosition} 
        });

      this.map.addLayer({
        'id': 'point',
        'source': 'point',
        'type': 'circle',
        'paint': {
          'circle-radius': 8,
          'circle-color': '#007cbf'
        }
      });
    });    
  }

  ngOnInit(): void {

    // TODO make server configurable
    this.socket = io('http://localhost:5001', { transports: ['websocket']});
    this.socket.on("connect", (socket) => this.onConnection(socket));
    this.socket.on("navigationInit", (data) => this.onNavigationInit(data));
    this.socket.on("positionUpdates", (data) => this.onPositionUpdates(data));
    return

    // TODO import { environment } from '../../../environments/environment';
    // TODO mapboxgl.accessToken = environment.mapbox.accessToken;
    var startingPosition = [33.05986, 34.70234];
    mapboxgl.accessToken = 'pk.eyJ1Ijoia29zdGFza2dyIiwiYSI6ImNraWF1bGw1bjBzeDcyc2xidmJ5NHA5NDkifQ.txJo3lqZ7Pw8jHVfZUTN2g'
    this.map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/streets-v11',
      zoom: 15,
      center: startingPosition
    });

    this.map.addControl(new mapboxgl.NavigationControl());

    this.map.on('load', () => {

      // https://docs.mapbox.com/mapbox-gl-js/example/geojson-line/
      this.map.addSource('route', {
        'type': 'geojson',
        'data': this.data
      });

      this.map.addLayer({
        'id': 'route',
        'type': 'line',
        'source': 'route',
        'layout': {
          'line-join': 'round',
          'line-cap': 'round'
        },
        'paint': {
          'line-color': '#0c8ced',
          'line-width': 4
        }
      });


      this.map.addSource('point', {
        'type': 'geojson',
        'data': {
          'type': 'Point',
          'coordinates': startingPosition} 
        });

      this.map.addLayer({
        'id': 'point',
        'source': 'point',
        'type': 'circle',
        'paint': {
          'circle-radius': 8,
          'circle-color': '#007cbf'
        }
      });

      // window.setInterval(() => {
      //   this.fly()

      // }, 5000);
    });
  }
}