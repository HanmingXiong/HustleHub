import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

type AuthMode = 'login' | 'register';
type UserRole = 'applicant' | 'employer';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css'],
})
export class AuthComponent {
  mode: AuthMode = 'login';
  backendUrl = 'http://localhost:8000';
  registering = false;
  loggingIn = false;
  message = '';
  error = '';

  registerData = {
    username: '',
    email: '',
    password: '',
    role: 'applicant' as UserRole,
  };

  loginData = {
    email: '',
    password: '',
  };

  constructor(private http: HttpClient, private router: Router) {}

  switchMode(mode: AuthMode) {
    this.mode = mode;
    this.message = '';
    this.error = '';
  }

  register() {
    this.registering = true;
    this.message = '';
    this.error = '';

    this.http
      .post(`${this.backendUrl}/auth/register`, this.registerData, {
        withCredentials: true,
      })
      .subscribe({
        next: (res: any) => {
          this.message = `Registered ${res.username} as ${res.role}`;
          this.registering = false;
        },
        error: (err) => {
          this.error = err?.error?.detail || 'Registration failed';
          this.registering = false;
        },
      });
  }

  login() {
    this.loggingIn = true;
    this.message = '';
    this.error = '';

    this.http
      .post(`${this.backendUrl}/auth/login`, this.loginData, {
        withCredentials: true,
      })
      .subscribe({
        next: (res: any) => {
          this.message = `Logged in as ${res.username}`;
          this.loggingIn = false;
          this.router.navigateByUrl('/home');
        },
        error: (err) => {
          this.error = err?.error?.detail || 'Login failed';
          this.loggingIn = false;
        },
      });
  }
}
