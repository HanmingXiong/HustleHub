import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Router, RouterLink, RouterOutlet, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  
  imports: [CommonModule, RouterLink, RouterOutlet],
  
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'hustle-hub-app';
  currentUser: { username: string } | null = null;

  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit(): void {
    this.refreshUser();
    this.router.events
      .pipe(filter((evt): evt is NavigationEnd => evt instanceof NavigationEnd))
      .subscribe(() => this.refreshUser());
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
      .get<{ username: string }>('http://localhost:8000/auth/me', { withCredentials: true })
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
