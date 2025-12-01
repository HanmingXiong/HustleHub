import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService, RegisterData, LoginData } from '../../services/auth.service'

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
  mode: 'login' | 'register' = 'login';
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

  constructor(private http: HttpClient, private router: Router, private authService: AuthService) {}

  switchMode(mode: AuthMode) {
    this.mode = mode;
    this.message = '';
    this.error = '';
  }

  register() {
    this.registering = true;
    this.message = '';
    this.error = '';

    this.authService.register(this.registerData).subscribe({
      next: (user) => {
        this.message = `Registered ${user.username} as ${user.role}`;
        this.registering = false;
        // Optional: auto-login or switch tab here
      },
      error: (err) => {
        this.error = err?.error?.detail || 'Registration failed';
        this.registering = false;
      }
    });
  }

  login() {
    this.loggingIn = true;
    this.message = '';
    this.error = '';

    this.authService.login(this.loginData).subscribe({
      next: (user) => {
        this.message = `Logged in as ${user.username}`;
        this.loggingIn = false;
        this.router.navigateByUrl('/home');
      },
      error: (err) => {
        this.error = err?.error?.detail || 'Login failed';
        this.loggingIn = false;
      }
    });
  }
}
