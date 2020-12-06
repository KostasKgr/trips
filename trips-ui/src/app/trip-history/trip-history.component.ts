import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-trip-history',
  templateUrl: './trip-history.component.html',
  styleUrls: ['./trip-history.component.css']
})
export class TripHistoryComponent implements OnInit {

  constructor() { }

  trips = [];

  ngOnInit(): void {

    fetch("http://localhost:5001/trips")
      .then(response => response.json())
      .then(data => { this.trips = data.trips; console.log(this.trips); });

  }

}
