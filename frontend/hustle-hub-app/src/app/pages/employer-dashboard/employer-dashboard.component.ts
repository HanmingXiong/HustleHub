import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

interface Applicant {
  application_id: number;
  applicant_name: string;
  applicant_email: string;
  job_title: string;
  cover_letter: string;
  resume_file: string | null;
  status: string;
  date_applied: string;
}

@Component({
  selector: 'app-employer-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './employer-dashboard.component.html',
  styleUrls: ['./employer-dashboard.component.css']
})
export class EmployerDashboardComponent implements OnInit {
  applicants: Applicant[] = [];
  isLoading = true;
  message = '';

  // Allowed statuses for employer updates
  statuses = ['pending', 'reviewed', 'accepted', 'rejected'];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.fetchApplicants();
  }

  fetchApplicants() {
    this.http.get<Applicant[]>('http://localhost:8000/jobs/employer/applications', { withCredentials: true })
      .subscribe({
        next: (data) => {
          this.applicants = data;
          this.isLoading = false;
        },
        error: (err) => {
          console.error(err);
          this.isLoading = false;
        }
      });
  }

  updateStatus(app: Applicant, newStatus: string) {
    const payload = { status: newStatus };
    
    this.http.put(`http://localhost:8000/jobs/applications/${app.application_id}/status`, payload, { withCredentials: true })
      .subscribe({
        next: () => {
          app.status = newStatus;
          this.message = `Updated status to ${newStatus}`;
          setTimeout(() => this.message = '', 3000);
        },
        error: (err) => {
          console.error('Update failed', err);
          alert('Failed to update status');
        }
      });
  }
}
