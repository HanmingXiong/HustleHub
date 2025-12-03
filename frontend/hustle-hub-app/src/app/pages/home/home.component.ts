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

  isEmployer: boolean = false;
  
  private userSub: Subscription | undefined;

  constructor(private http: HttpClient, private router: Router, public authService: AuthService) {}

  ngOnInit() {
    this.userSub = this.authService.currentUser$.subscribe((user: User | null) => {
      this.isEmployer = user?.role === 'employer';
    });

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
    this.http.get<Job[]>('http://localhost:8000/jobs') 
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

  filterJobs() {
    // Client-side filter by title and location
    this.filteredJobs = this.jobs.filter(job => {
      const matchTitle = job.title.toLowerCase().includes(this.searchTerm.toLowerCase());
      const matchLocation = job.location.toLowerCase().includes(this.searchLocation.toLowerCase());
      return matchTitle && matchLocation;
    });
  }

  navigateToCreateJob() {
    this.router.navigate(['/create-job']);
  }

  navigateToApply(jobId: number) {
    this.router.navigate(['/apply', jobId]);
  }
}
