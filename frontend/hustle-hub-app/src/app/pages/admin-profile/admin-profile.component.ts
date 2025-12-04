import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-admin-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './admin-profile.component.html',
  styleUrl: './admin-profile.component.css'
})
export class AdminProfileComponent implements OnInit {
  profileForm: FormGroup;
  companyForm: FormGroup;
  user: any = null;
  employer: any = null;
  isEditMode = false;
  isEditCompanyMode = false;
  isSaving = false;
  isSavingCompany = false;
  isLoading = false;
  isUploadingResume = false;
  selectedFile: File | null = null;
  message = '';
  messageType: 'success' | 'error' = 'success';
  
  // Password change state
  currentPassword = '';
  newPassword = '';
  confirmPassword = '';
  isChangingPassword = false;
  showCurrentPassword = false;
  showNewPassword = false;
  showConfirmPassword = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private api: ApiService
  ) {
    this.profileForm = this.fb.group({
      username: ['', Validators.required],
      first_name: [''],
      last_name: [''],
      email: ['', [Validators.required, Validators.email]],
      phone: ['']
    });

    this.companyForm = this.fb.group({
      company_name: ['', Validators.required],
      description: [''],
      website: [''],
      location: ['']
    });
  }

  ngOnInit() {
    this.loadProfile();
  }

  loadProfile() {
    this.isLoading = true;
    this.api.get<any>('/profile/me').subscribe({
      next: (user) => {
        this.user = user;
        this.profileForm.patchValue(user);
        this.isLoading = false;
        
        // Load employer info
        this.loadEmployerInfo();
      },
      error: () => {
        this.showMessage('Failed to load profile', 'error');
        this.isLoading = false;
      }
    });
  }

  loadEmployerInfo() {
    this.api.get<any>('/employers/me').subscribe({
      next: (employer) => {
        this.employer = employer;
        this.companyForm.patchValue(employer);
      },
      error: () => {
        // Employer record doesn't exist yet
        this.employer = null;
      }
    });
  }

  saveCompanyInfo() {
    if (this.companyForm.valid) {
      this.isSavingCompany = true;
      const endpoint = this.employer ? '/employers/me' : '/employers';
      const method = this.employer ? 'put' : 'post';
      
      this.api[method](endpoint, this.companyForm.value).subscribe({
        next: (employer: any) => {
          this.employer = employer;
          this.isEditCompanyMode = false;
          this.isSavingCompany = false;
          this.showMessage('Company information updated!', 'success');
        },
        error: () => {
          this.showMessage('Failed to update company information', 'error');
          this.isSavingCompany = false;
        }
      });
    }
  }

  saveProfile() {
    if (this.profileForm.valid) {
      this.isSaving = true;
      this.api.put('/profile/me', this.profileForm.value).subscribe({
        next: (user: any) => {
          this.user = user;
          this.isEditMode = false;
          this.isSaving = false;
          this.showMessage('Profile updated!', 'success');
        },
        error: () => {
          this.showMessage('Failed to update profile', 'error');
          this.isSaving = false;
        }
      });
    }
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      const allowed = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!allowed.includes(file.type)) {
        this.showMessage('Only PDF, DOC, DOCX allowed', 'error');
        return;
      }
      this.selectedFile = file;
      this.uploadResume();
    }
  }

  uploadResume() {
    if (!this.selectedFile) return;

    this.isUploadingResume = true;
    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.api.post('/profile/resume', formData).subscribe({
      next: () => {
        this.loadProfile();
        this.selectedFile = null;
        this.isUploadingResume = false;
        this.showMessage('Resume uploaded!', 'success');
      },
      error: () => {
        this.showMessage('Failed to upload resume', 'error');
        this.isUploadingResume = false;
      }
    });
  }

  deleteResume() {
    if (!confirm('Delete your resume?')) return;

    this.api.delete('/profile/resume').subscribe({
      next: () => {
        this.user.resume_file = null;
        this.showMessage('Resume deleted', 'success');
      },
      error: () => {
        this.showMessage('Failed to delete resume', 'error');
      }
    });
  }

  getInitials(): string {
    const first = this.user?.first_name?.charAt(0) || '';
    const last = this.user?.last_name?.charAt(0) || '';
    return (first + last).toUpperCase() || this.user?.username?.substring(0, 2).toUpperCase() || '??';
  }

  getFullName(): string {
    const fullName = `${this.user?.first_name || ''} ${this.user?.last_name || ''}`.trim();
    return fullName || this.user?.username || 'Loading...';
  }

  getResumeFileName(): string {
    return this.user?.resume_file?.split('/').pop() || '';
  }

  changePassword() {
    if (!this.currentPassword || !this.newPassword || !this.confirmPassword) {
      this.showMessage('Please fill all password fields', 'error');
      return;
    }

    if (this.newPassword !== this.confirmPassword) {
      this.showMessage('New passwords do not match', 'error');
      return;
    }

    if (this.newPassword.length < 6) {
      this.showMessage('Password must be at least 6 characters', 'error');
      return;
    }

    this.isChangingPassword = true;
    this.api.put('/profile/change-password', {
      current_password: this.currentPassword,
      new_password: this.newPassword
    }).subscribe({
      next: () => {
        this.currentPassword = '';
        this.newPassword = '';
        this.confirmPassword = '';
        this.isChangingPassword = false;
        this.showMessage('Password changed successfully!', 'success');
      },
      error: (error: any) => {
        const errorMsg = error.error?.detail || 'Failed to change password';
        this.showMessage(errorMsg, 'error');
        this.isChangingPassword = false;
      }
    });
  }

  showMessage(msg: string, type: 'success' | 'error') {
    this.message = msg;
    this.messageType = type;
    setTimeout(() => this.message = '', 3000);
  }
}
