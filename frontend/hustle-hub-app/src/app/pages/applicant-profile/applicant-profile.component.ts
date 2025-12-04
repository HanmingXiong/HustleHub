import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-applicant-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './applicant-profile.component.html',
  styleUrl: './applicant-profile.component.css'
})
export class ApplicantProfileComponent implements OnInit {
  profileForm: FormGroup;
  user: any = null;
  isEditMode = false;
  isSaving = false;
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

  // Delete account state
  showDeleteModal = false;
  deletePassword = '';
  showDeletePassword = false;
  isDeletingAccount = false;

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
      },
      error: () => {
        this.showMessage('Failed to load profile', 'error');
        this.isLoading = false;
      }
    });
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

  openDeleteModal() {
    this.showDeleteModal = true;
    this.deletePassword = '';
  }

  closeDeleteModal() {
    this.showDeleteModal = false;
    this.deletePassword = '';
  }

  confirmDeleteAccount() {
    if (!this.deletePassword) {
      this.showMessage('Please enter your password', 'error');
      return;
    }

    this.isDeletingAccount = true;
    this.api.delete(`/profile/delete-account?password=${encodeURIComponent(this.deletePassword)}`).subscribe({
      next: () => {
        this.showMessage('Account deleted successfully', 'success');
        setTimeout(() => {
          this.authService.logout().subscribe(() => {
            this.router.navigate(['/auth']);
          });
        }, 1500);
      },
      error: (error: any) => {
        const errorMsg = error.error?.detail || 'Failed to delete account';
        this.showMessage(errorMsg, 'error');
        this.isDeletingAccount = false;
        this.deletePassword = '';
      }
    });
  }

  showMessage(msg: string, type: 'success' | 'error') {
    this.message = msg;
    this.messageType = type;
    setTimeout(() => this.message = '', 3000);
  }
}
