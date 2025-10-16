import { Component, OnInit, importProvidersFrom } from '@angular/core';
import { HttpClient, provideHttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  standalone: true,        // important for standalone components
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'hustle-hub-app';
  message: string | null = null;
  error: string | null = null;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.http.get<{ message: string }>('http://127.0.0.1:8000/')
      .subscribe({
        next: (response) => {
          this.message = response.message;
        },
        error: (err) => {
          this.error = "Failed to connect to backend"
          console.error('Error fetching message:', err);
        }
      });
  }
}
