import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-apply-job',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './apply-job.component.html',
  styleUrls: ['./apply-job.component.css'] // Use the same CSS file or copy it
})
export class ApplyJobComponent implements OnInit {
  jobId: string | null = null;
  // so know waiting for the job to fully load
  jobTitle: string = 'Loading...';
  coverLetter: string = '';
  
  isSubmitting = false;
  message = '';
  error = '';

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    // get the id from the url
    this.jobId = this.route.snapshot.paramMap.get('id');
    
    // get specific job details
    if (this.jobId) {
      this.http.get<any>(`http://localhost:8000/jobs/${this.jobId}`).subscribe({
        next: (job) => {
          this.jobTitle = job.title;
        },
        error: () => {
          this.jobTitle = 'Job not found';
          this.error = 'Could not load job details.';
        }
      });
    }
  }

  // what the button will call
  submitApplication() {
    if (!this.jobId) return;

    this.isSubmitting = true;
    this.error = '';
    this.message = '';

    const payload = { cover_letter: this.coverLetter };

    this.http.post(`http://localhost:8000/jobs/${this.jobId}/apply`, payload, { withCredentials: true })
      .subscribe({
        next: () => {
          this.message = 'Application submitted successfully!';
          this.isSubmitting = false;
          // redirect to home page
          setTimeout(() => this.router.navigate(['/home']), 2000);
        },
        error: (err) => {
          this.isSubmitting = false;
          this.error = err.error?.detail || 'Application failed';
        }
      });
  }
}