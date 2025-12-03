import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-employer-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './employer-profile.component.html',
  styleUrl: './employer-profile.component.css'
})
export class EmployerProfileComponent implements OnInit {
  profileForm: FormGroup;
  user: any = null;
  isEditMode = false;
  isSaving = false;
  isLoading = false;
  message = '';
  messageType: 'success' | 'error' = 'success';

  constructor(
    private fb: FormBuilder,
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

  getInitials(): string {
    const first = this.user?.first_name?.charAt(0) || '';
    const last = this.user?.last_name?.charAt(0) || '';
    return (first + last).toUpperCase() || this.user?.username?.substring(0, 2).toUpperCase() || '??';
  }

  getFullName(): string {
    const fullName = `${this.user?.first_name || ''} ${this.user?.last_name || ''}`.trim();
    return fullName || this.user?.username || 'Loading...';
  }

  // Password change state
  currentPassword = '';
  newPassword = '';
  confirmPassword = '';
  isChangingPassword = false;
  showCurrentPassword = false;
  showNewPassword = false;
  showConfirmPassword = false;

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
