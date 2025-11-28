import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';

interface User {
  user_id: number;
  username: string;
  email: string;
  role: 'applicant' | 'employer' | 'admin';
  firstName: string;
  lastName: string;
  headline: string;
  location: string;
  phone: string;
  profileImage?: string;
}

interface Education {
  id: number;
  school: string;
  degree: string;
  field?: string;
  startDate: string;
  endDate: string;
  gpa?: string;
}

interface Experience {
  id: number;
  title: string;
  company: string;
  location: string;
  startDate: string;
  endDate: string;
  current: boolean;
  description: string;
}

interface Skill {
  id: number;
  name: string;
}

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit {
  profileForm: FormGroup;
  isEditMode = false;
  isSaving = false;
  isLoading = false;
  showSuccessMessage = false;
  showErrorMessage = false;
  errorMessage = '';

  // Mock user data
  user: User = {
    user_id: 1,
    username: 'johndoe',
    email: 'john.doe@hustlehub.com',
    role: 'applicant',
    firstName: 'John',
    lastName: 'Doe',
    headline: 'Experienced Delivery Driver | Seeking Warehouse Opportunities',
    location: 'San Francisco, CA',
    phone: '(555) 123-4567'
  };

  education: Education[] = [
    {
      id: 1,
      school: 'Mission High School',
      degree: 'High School Diploma',
      field: '',
      startDate: '2018',
      endDate: '2022',
      gpa: ''
    }
  ];

  experience: Experience[] = [
    {
      id: 1,
      title: 'Delivery Driver',
      company: 'DoorDash',
      location: 'San Francisco, CA',
      startDate: 'January 2023',
      endDate: '',
      current: true,
      description: 'Deliver food orders to customers throughout the Bay Area. Maintain 4.9 star rating with excellent customer service and timely deliveries.'
    },
    {
      id: 2,
      title: 'Warehouse Associate',
      company: 'Amazon Fulfillment Center',
      location: 'San Francisco, CA',
      startDate: 'June 2022',
      endDate: 'December 2022',
      current: false,
      description: 'Picked, packed, and shipped customer orders. Operated forklifts and pallet jacks. Consistently met daily productivity targets.'
    }
  ];

  skills: Skill[] = [
    { id: 1, name: 'Forklift Certified' },
    { id: 2, name: 'Customer Service' },
    { id: 3, name: 'Time Management' },
    { id: 4, name: 'Valid Driver\'s License' },
    { id: 5, name: 'Physical Stamina' },
    { id: 6, name: 'Reliable Transportation' }
  ];

  activeSection: string = 'profile';

  private originalFormValues: any;

  constructor(private fb: FormBuilder) {
    this.profileForm = this.fb.group({
      firstName: ['', Validators.required],
      lastName: ['', Validators.required],
      headline: ['', Validators.required],
      location: ['', Validators.required],
      phone: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]]
    });
  }

  setActiveSection(section: string) {
    this.activeSection = section;
  }

  ngOnInit() {
    console.log('Profile component loaded!');
    console.log('User data:', this.user);
    this.loadUserProfile();
  }

  loadUserProfile() {
    // Using mock data - replace with API call when ready
    this.updateForm();
  }

  updateForm() {
    this.profileForm.patchValue({
      firstName: this.user.firstName,
      lastName: this.user.lastName,
      headline: this.user.headline,
      location: this.user.location,
      phone: this.user.phone,
      email: this.user.email
    });
    this.originalFormValues = this.profileForm.value;
  }

  toggleEditMode() {
    this.isEditMode = !this.isEditMode;
    if (!this.isEditMode) {
      this.cancelEdit();
    }
  }

  cancelEdit() {
    this.isEditMode = false;
    this.profileForm.patchValue(this.originalFormValues);
    this.profileForm.markAsPristine();
    this.profileForm.markAsUntouched();
  }

  saveProfile() {
    if (this.profileForm.valid) {
      this.isSaving = true;

      // Simulate API call
      setTimeout(() => {
        // Update local user object
        this.user = {
          ...this.user,
          ...this.profileForm.value
        };

        this.originalFormValues = this.profileForm.value;
        this.isEditMode = false;
        this.isSaving = false;
        this.showSuccess();
      }, 1000);
    } else {
      Object.keys(this.profileForm.controls).forEach(key => {
        this.profileForm.get(key)?.markAsTouched();
      });
    }
  }

  getInitials(): string {
    return (this.user.firstName.charAt(0) + this.user.lastName.charAt(0)).toUpperCase();
  }

  getFullName(): string {
    return `${this.user.firstName} ${this.user.lastName}`;
  }

  // Helper to display role as account type
  getAccountType(): string {
    // Capitalize first letter: "applicant" → "Applicant"
    return this.user.role.charAt(0).toUpperCase() + this.user.role.slice(1);
  }

  // Check if user is employer
  isEmployer(): boolean {
    return this.user.role === 'employer';
  }

  // Check if user is applicant
  isApplicant(): boolean {
    return this.user.role === 'applicant';
  }

  private showSuccess() {
    this.showSuccessMessage = true;
    setTimeout(() => {
      this.showSuccessMessage = false;
    }, 3000);
  }

  private showError(message: string) {
    this.errorMessage = message;
    this.showErrorMessage = true;
    setTimeout(() => {
      this.showErrorMessage = false;
    }, 3000);
  }
}
