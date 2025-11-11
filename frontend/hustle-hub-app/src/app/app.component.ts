import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

// 1. Import RouterLink and RouterOutlet
import { RouterLink, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  
  imports: [CommonModule, RouterLink, RouterOutlet],
  
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'hustle-hub-app';
  constructor() {}
}