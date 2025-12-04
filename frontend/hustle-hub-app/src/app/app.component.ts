import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Router, RouterLink, RouterOutlet, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { AuthService } from './services/auth.service';


@Component({
  selector: 'app-root',
  standalone: true,
  
  imports: [CommonModule, RouterLink, RouterOutlet],
  
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'Hustle Hub';
  currentUser: { username: string; role: string } | null = null;

  constructor(private http: HttpClient, private router: Router, public authService: AuthService) {}

  ngOnInit(): void {
    this.refreshUser();
    this.router.events
      .pipe(filter((evt): evt is NavigationEnd => evt instanceof NavigationEnd))
      .subscribe(() => this.refreshUser());
    this.authService.currentUser$.subscribe(user => {
        if (user !== undefined) {
          this.currentUser = user;
        }
      });
  }

  getProfileRoute(): string {
    if (!this.currentUser) return '/auth';
    return `/profile/${this.currentUser.role}`;
  }

  logout() {
    this.http
      .post('http://localhost:8000/auth/logout', {}, { withCredentials: true })
      .subscribe({
        next: () => {
          this.currentUser = null;
          window.location.href = '/auth';
        },
        error: () => {
          this.currentUser = null;
          window.location.href = '/auth';
        },
      });
  }

  private refreshUser() {
    this.http
      .get<{ username: string; role: string }>('http://localhost:8000/auth/me', { withCredentials: true })
      .subscribe({
        next: (user) => {
          this.currentUser = user;
        },
        error: () => {
          this.currentUser = null;
        },
      });
  }
}
