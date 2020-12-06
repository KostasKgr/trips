import { Component, OnInit } from '@angular/core';
import { environment } from '../../environments/environment';
@Component({
  selector: 'app-trip-history',
  templateUrl: './trip-history.component.html',
  styleUrls: ['./trip-history.component.css']
})
export class TripHistoryComponent implements OnInit {

  constructor() { }

  trips = [];

  ngOnInit(): void {

    fetch(environment.tripsServiceUrl + "/trips")
      .then(response => response.json())
      .then(data => { this.trips = data.trips; console.log(this.trips); });

  }

}
