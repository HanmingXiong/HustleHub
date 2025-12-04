import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

interface User {
  user_id: number;
  username: string;
  email: string;
  role: string;
  first_name: string | null;
  last_name: string | null;
  phone: string | null;
  created_at: string;
}

interface Job {
  job_id: number;
  employer_id: number;
  company_name: string;
  title: string;
  description: string;
  job_type: string;
  location: string;
  pay_range: string | null;
  is_active: boolean;
  date_posted: string;
}

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css']
})
export class AdminDashboardComponent implements OnInit {
  users: User[] = [];
  jobs: Job[] = [];
  currentUserId: number | null = null;
  isLoadingUsers = true;
  isLoadingJobs = true;
  message = '';
  messageType: 'success' | 'error' = 'success';
  activeTab: 'users' | 'jobs' = 'users';
  
  showAddUserModal = false;
  showPasswordVerifyModal = false;
  showDeleteConfirmModal = false;
  adminPassword = '';
  deletePassword = '';
  pendingAdminCreation = false;
  pendingDeleteAction: (() => void) | null = null;
  deleteTargetName = '';
  newUser = {
    username: '',
    email: '',
    password: '',
    role: 'applicant'
  };

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.fetchCurrentUser();
    this.fetchUsers();
    this.fetchJobs();
  }

  fetchCurrentUser() {
    this.http.get<any>('http://localhost:8000/auth/me', { withCredentials: true })
      .subscribe({
        next: (user) => {
          this.currentUserId = user.user_id;
        },
        error: (err) => {
          console.error('Failed to get current user', err);
        }
      });
  }

  fetchUsers() {
    this.http.get<User[]>('http://localhost:8000/admin/users', { withCredentials: true })
      .subscribe({
        next: (data) => {
          this.users = data;
          this.isLoadingUsers = false;
        },
        error: (err) => {
          console.error(err);
          this.showMessage('Failed to load users', 'error');
          this.isLoadingUsers = false;
        }
      });
  }

  fetchJobs() {
    this.http.get<Job[]>('http://localhost:8000/admin/jobs', { withCredentials: true })
      .subscribe({
        next: (data) => {
          this.jobs = data;
          this.isLoadingJobs = false;
        },
        error: (err) => {
          console.error(err);
          this.showMessage('Failed to load jobs', 'error');
          this.isLoadingJobs = false;
        }
      });
  }

  openDeleteUserModal(userId: number, username: string) {
    this.deleteTargetName = `user "${username}"`;
    this.pendingDeleteAction = () => this.executeDeleteUser(userId);
    this.showDeleteConfirmModal = true;
  }

  openDeleteJobModal(jobId: number, jobTitle: string) {
    this.deleteTargetName = `job "${jobTitle}"`;
    this.pendingDeleteAction = () => this.executeDeleteJob(jobId);
    this.showDeleteConfirmModal = true;
  }

  closeDeleteConfirmModal() {
    this.showDeleteConfirmModal = false;
    this.deletePassword = '';
    this.pendingDeleteAction = null;
    this.deleteTargetName = '';
  }

  async confirmDelete() {
    if (!this.deletePassword) {
      this.showMessage('Please enter your admin password', 'error');
      return;
    }

    // Verify admin password
    const verified = await this.verifyAdminPassword(this.deletePassword);
    if (!verified) {
      this.showMessage('Incorrect admin password', 'error');
      this.deletePassword = '';
      return;
    }

    // Execute the pending delete action
    if (this.pendingDeleteAction) {
      this.pendingDeleteAction();
    }

    this.closeDeleteConfirmModal();
  }

  executeDeleteUser(userId: number) {
    this.http.delete(`http://localhost:8000/admin/users/${userId}`, { withCredentials: true })
      .subscribe({
        next: () => {
          this.users = this.users.filter(u => u.user_id !== userId);
          this.showMessage('User deleted successfully', 'success');
        },
        error: (err) => {
          console.error(err);
          this.showMessage(err.error?.detail || 'Failed to delete user', 'error');
        }
      });
  }

  executeDeleteJob(jobId: number) {
    this.http.delete(`http://localhost:8000/admin/jobs/${jobId}`, { withCredentials: true })
      .subscribe({
        next: () => {
          this.jobs = this.jobs.filter(j => j.job_id !== jobId);
          this.showMessage('Job deleted successfully', 'success');
        },
        error: (err) => {
          console.error(err);
          this.showMessage('Failed to delete job', 'error');
        }
      });
  }

  openAddUserModal() {
    this.showAddUserModal = true;
    this.newUser = {
      username: '',
      email: '',
      password: '',
      role: 'applicant'
    };
  }

  closeAddUserModal() {
    this.showAddUserModal = false;
  }

  addUser() {
    if (!this.newUser.username || !this.newUser.email || !this.newUser.password) {
      this.showMessage('Please fill all required fields', 'error');
      return;
    }

    // Require admin password verification when creating admin account
    if (this.newUser.role === 'admin') {
      this.showPasswordVerifyModal = true;
      return;
    }

    this.createUser();
  }

  async confirmAdminCreation() {
    if (!this.adminPassword) {
      this.showMessage('Please enter your admin password', 'error');
      return;
    }

    // Verify admin password
    const verified = await this.verifyAdminPassword(this.adminPassword);
    if (!verified) {
      this.showMessage('Incorrect admin password. Admin account creation cancelled.', 'error');
      this.adminPassword = '';
      return;
    }

    this.showPasswordVerifyModal = false;
    this.adminPassword = '';
    this.createUser();
  }

  cancelPasswordVerify() {
    this.showPasswordVerifyModal = false;
    this.adminPassword = '';
  }

  createUser() {
    this.http.post<User>('http://localhost:8000/admin/users', this.newUser, { withCredentials: true })
      .subscribe({
        next: (user) => {
          this.users.unshift(user);
          this.showMessage('User created successfully', 'success');
          this.closeAddUserModal();
        },
        error: (err) => {
          console.error(err);
          this.showMessage(err.error?.detail || 'Failed to create user', 'error');
        }
      });
  }

  verifyAdminPassword(password: string): Promise<boolean> {
    return new Promise((resolve) => {
      this.http.post<any>('http://localhost:8000/admin/verify-password', 
        { password }, 
        { withCredentials: true }
      ).subscribe({
        next: (response) => {
          resolve(response.valid === true);
        },
        error: () => {
          resolve(false);
        }
      });
    });
  }

  showMessage(msg: string, type: 'success' | 'error') {
    this.message = msg;
    this.messageType = type;
    setTimeout(() => this.message = '', 3000);
  }
}
