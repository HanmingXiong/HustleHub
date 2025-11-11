import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common'; // Import CommonModule

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule], // Add CommonModule here
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit { // Implement OnInit
  
  // Properties to hold the response or error
  message: string | null = null;
  error: string | null = null;

  // Inject HttpClient here
  constructor(private http: HttpClient) {}

  // The http.get() logic now lives here
  ngOnInit() {
    this.http.get<{ message: string }>('http://127.0.0.1:8000/')
      .subscribe({
        next: (response) => {
          this.message = response.message;
        },
        error: (err) => {
          this.error = "Failed to connect to backend";
          console.error('Error fetching message:', err);
        }
      });
  }
}