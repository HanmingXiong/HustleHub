import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

interface Applicant {
  application_id: number;
  applicant_name: string;
  applicant_email: string;
  applicant_user_id: number;
  job_title: string;
  cover_letter: string;
  resume_file: string | null;
  status: string;
  date_applied: string;
}

interface Job {
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
  application_count: number;
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
  jobs: Job[] = [];
  isLoading = true;
  isLoadingJobs = true;
  message = '';
  messageType: 'success' | 'error' = 'success';
  hasCompanyInfo: boolean = true;
  showCreateJobModal = false;
  showCandidatesModal = false;
  isCreatingJob = false;
  jobError = '';
  selectedJobId: number | null = null;
  selectedJobTitle: string = '';
  candidatesForJob: Applicant[] = [];
  activeTab: 'applications' | 'jobs' = 'applications';
  newJob = {
    title: '',
    description: '',
    job_type: 'full-time',
    location: '',
    pay_range: ''
  };

  // Allowed statuses for employer updates
  statuses = ['pending', 'reviewed', 'accepted', 'rejected'];

  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit() {
    this.checkCompanyInfo();
    this.fetchApplicants();
    this.fetchJobs();
  }

  checkCompanyInfo() {
    this.http.get<any>('http://localhost:8000/employers/me', { withCredentials: true })
      .subscribe({
        next: (employer) => {
          this.hasCompanyInfo = !!(employer && employer.company_name);
        },
        error: () => {
          this.hasCompanyInfo = false;
        }
      });
  }

  openCreateJobModal() {
    if (!this.hasCompanyInfo) {
      this.showMessage('Please complete your company information in your profile before posting jobs', 'error');
      return;
    }
    this.showCreateJobModal = true;
    this.newJob = {
      title: '',
      description: '',
      job_type: 'full-time',
      location: '',
      pay_range: ''
    };
  }

  closeCreateJobModal() {
    this.showCreateJobModal = false;
    this.jobError = '';
  }

  createJob() {
    if (!this.newJob.title || !this.newJob.description || !this.newJob.location) {
      this.jobError = 'Please fill all required fields';
      return;
    }

    this.isCreatingJob = true;
    this.jobError = '';

    this.http.post('http://localhost:8000/jobs/', this.newJob, { withCredentials: true })
      .subscribe({
        next: () => {
          this.isCreatingJob = false;
          this.showMessage('Job posted successfully!', 'success');
          this.closeCreateJobModal();
          this.activeTab = 'jobs'; // Switch to My Jobs tab
          this.fetchJobs(); // Refresh the jobs list
        },
        error: (err) => {
          this.isCreatingJob = false;
          this.jobError = err.error?.detail || 'Failed to create job';
        }
      });
  }

  navigateToProfile() {
    this.router.navigate(['/profile/employer']);
  }

  showMessage(msg: string, type: 'success' | 'error') {
    this.message = msg;
    this.messageType = type;
    setTimeout(() => this.message = '', 3000);
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

  openCandidatesModal(jobId: number, jobTitle: string) {
    this.selectedJobId = jobId;
    this.selectedJobTitle = jobTitle;
    
    // Fetch applications for this specific job
    this.http.get<Applicant[]>(`http://localhost:8000/jobs/employer/applications/${jobId}`, { withCredentials: true })
      .subscribe({
        next: (data) => {
          this.candidatesForJob = data;
          this.showCandidatesModal = true;
        },
        error: (err) => {
          console.error('Error fetching candidates', err);
          this.showMessage('Failed to load candidates', 'error');
        }
      });
  }

  closeCandidatesModal() {
    this.showCandidatesModal = false;
    this.selectedJobId = null;
    this.selectedJobTitle = '';
    this.candidatesForJob = [];
  }

  getApplicationCount(jobTitle: string): number {
    return this.applicants.filter(app => app.job_title === jobTitle).length;
  }

  fetchJobs() {
    this.http.get<Job[]>('http://localhost:8000/jobs/employer/jobs', { withCredentials: true })
      .subscribe({
        next: (data) => {
          this.jobs = data;
          this.isLoadingJobs = false;
        },
        error: (err) => {
          console.error(err);
          this.isLoadingJobs = false;
        }
      });
  }

  updateStatus(app: Applicant, newStatus: string) {
    const payload = { status: newStatus };
    
    this.http.put(`http://localhost:8000/jobs/applications/${app.application_id}/status`, payload, { withCredentials: true })
      .subscribe({
        next: () => {
          app.status = newStatus;
          this.showMessage(`Updated status to ${newStatus}`, 'success');
        },
        error: (err) => {
          console.error('Update failed', err);
          this.showMessage('Failed to update status', 'error');
        }
      });
  }

  toggleJobActive(job: Job) {
    this.http.put(`http://localhost:8000/jobs/${job.job_id}/toggle-active`, {}, { withCredentials: true })
      .subscribe({
        next: (response: any) => {
          job.is_active = response.is_active;
          this.showMessage(job.is_active ? 'Job activated' : 'Job deactivated', 'success');
        },
        error: (err) => {
          console.error('Toggle failed', err);
          this.showMessage('Failed to update job status', 'error');
        }
      });
  }

  downloadResume(userId: number, applicantName: string) {
    window.open(`http://localhost:8000/profile/resume/${userId}`, '_blank');
  }
}
