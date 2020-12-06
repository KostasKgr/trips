import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { MapComponent } from './map/map.component';
import { TripHistoryComponent } from './trip-history/trip-history.component';

const routes: Routes = [
  { path: 'trips', component: TripHistoryComponent },
  { path: 'live', component: MapComponent },
  {path: '', redirectTo: '/live', pathMatch: 'full'},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
