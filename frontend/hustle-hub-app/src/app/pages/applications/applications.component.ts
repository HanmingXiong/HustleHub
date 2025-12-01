import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common'; // Necessary for *ngFor and *ngIf
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router'; // For routerLink if needed

interface Application {
  application_id: number;
  status: string;
  date_applied: string;
  job_title: string;
  company_name: string;
  job_id: number;
}

@Component({
  selector: 'app-applications',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './applications.component.html',
  styleUrls: ['./applications.component.css']
})
export class ApplicationsComponent implements OnInit {
  applications: Application[] = [];
  isLoading = true;
  error = '';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.fetchApplications();
  }

  fetchApplications() {
    this.http.get<Application[]>('http://localhost:8000/jobs/applications/me', { withCredentials: true })
      .subscribe({
        next: (data) => {
          this.applications = data;
          this.isLoading = false;
        },
        error: (err) => {
          console.error('Error fetching applications', err);
          this.error = 'Failed to load applications. Please log in.';
          this.isLoading = false;
        }
      });
  }
}