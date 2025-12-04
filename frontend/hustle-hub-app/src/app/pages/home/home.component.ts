import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthService, User } from '../../services/auth.service';

export interface Job {
  job_id: number;
  employer_id: number;
  company_name: string;
  title: string;
  description: string;
  job_type: string;
  location: string;
  pay_range: string;
  date_posted: string;
  is_active: boolean;
  has_applied: boolean;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule], 
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  
  jobs: Job[] = [];
  filteredJobs: Job[] = [];

  searchTerm: string = '';
  searchLocation: string = '';

  message = '';
  messageType: 'success' | 'error' = 'success';
  showWithdrawModal = false;
  jobToWithdraw: number | null = null;
  
  private userSub: Subscription | undefined;

  constructor(private http: HttpClient, private router: Router, public authService: AuthService) {}

  get isEmployer(): boolean {
    return this.authService.getCurrentUser()?.role === 'employer';
  }

  ngOnInit() {
    this.fetchJobs();
  }

  // Avoid leaking the auth subscription
  ngOnDestroy() {
    if (this.userSub) {
      this.userSub.unsubscribe();
    }
  }

  fetchJobs() {
    // Load active jobs with employer names for the landing grid
    this.http.get<Job[]>('http://localhost:8000/jobs', { withCredentials: true }) 
      .subscribe({
        next: (data) => {
          this.jobs = data;
          this.filteredJobs = data;
        },
        error: (err) => {
          console.error('Error fetching jobs:', err);
        }
      });
  }

  openWithdrawModal(jobId: number) {
    this.jobToWithdraw = jobId;
    this.showWithdrawModal = true;
  }

  closeWithdrawModal() {
    this.showWithdrawModal = false;
    this.jobToWithdraw = null;
  }

  confirmWithdraw() {
    if (!this.jobToWithdraw) return;

    this.http.delete(`http://localhost:8000/jobs/applications/withdraw/${this.jobToWithdraw}`, { withCredentials: true })
      .subscribe({
        next: () => {
          this.showMessage('Application withdrawn successfully', 'success');
          this.fetchJobs();
          this.closeWithdrawModal();
        },
        error: (err) => {
          console.error('Error withdrawing application:', err);
          this.showMessage('Failed to withdraw application', 'error');
          this.closeWithdrawModal();
        }
      });
  }

  showMessage(msg: string, type: 'success' | 'error') {
    this.message = msg;
    this.messageType = type;
    setTimeout(() => this.message = '', 3000);
  }

  filterJobs() {
    // Client-side filter by title and location
    this.filteredJobs = this.jobs.filter(job => {
      const matchTitle = job.title.toLowerCase().includes(this.searchTerm.toLowerCase());
      const matchLocation = job.location.toLowerCase().includes(this.searchLocation.toLowerCase());
      return matchTitle && matchLocation;
    });
  }

  navigateToApply(jobId: number) {
    this.router.navigate(['/apply', jobId]);
  }
}
