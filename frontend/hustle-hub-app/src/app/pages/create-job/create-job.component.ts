import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-create-job',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './create-job.component.html',
  styleUrls: ['./create-job.component.css']
})
export class CreateJobComponent {
  jobData = {
    title: '',
    description: '',
    job_type: 'full-time',
    location: '',
    pay_range: ''
  };

  isSubmitting = false;
  error = '';

  constructor(private http: HttpClient, private router: Router) {}

  createJob() {
    this.isSubmitting = true;
    this.error = '';

    // withCredentials true is important so backend knows who is logged in
    // makes sure the user is an employer
    this.http.post('http://localhost:8000/jobs/', this.jobData, { withCredentials: true })
      .subscribe({
        next: () => {
          this.isSubmitting = false;
          this.router.navigate(['/home']);
        },
        error: (err) => {
          this.isSubmitting = false;
          console.error(err);
          this.error = err.error?.detail || 'Failed to create job';
        }
      });
  }
}