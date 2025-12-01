import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthService, User } from '../../services/auth.service';

// job object that matches one defined in job schema
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

  // search + filter
  searchTerm: string = '';
  searchLocation: string = '';

  // switch for create job button
  isEmployer: boolean = false;
  
  // manage subscription for security
  private userSub: Subscription | undefined;

  constructor(private http: HttpClient, private router: Router, public authService: AuthService) {}

  ngOnInit() {
    this.userSub = this.authService.currentUser$.subscribe((user: User | null) => {
      this.isEmployer = user?.role === 'employer';
    });

    this.fetchJobs();
  }

  // unsub to prevent mem leak
  ngOnDestroy() {
    if (this.userSub) {
      this.userSub.unsubscribe();
    }
  }

  fetchJobs() {
    // We expect the backend to return a list of active jobs including company names
    this.http.get<Job[]>('http://localhost:8000/jobs') 
      .subscribe({
        next: (data) => {
          this.jobs = data;
          this.filteredJobs = data; // Initialize filtered list with all jobs
        },
        error: (err) => {
          console.error('Error fetching jobs:', err);
        }
      });
  }

  // filter logic for Title and Location
  filterJobs() {
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