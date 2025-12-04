import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { ApiService } from './api.service';

export interface User {
  user_id: number;
  username: string;
  email: string;
  role: 'applicant' | 'employer' | 'admin';
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  role: 'applicant' | 'employer';
}

export interface LoginData {
  email: string;
  password: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null | undefined>(undefined);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private api: ApiService) {
    this.checkAuth();
  }

  register(data: RegisterData): Observable<User> {
    return this.api.post<User>('/auth/register', data).pipe(
      tap(user => this.currentUserSubject.next(user))
    );
  }

  login(data: LoginData): Observable<User> {
    return this.api.post<User>('/auth/login', data).pipe(
      tap(user => this.currentUserSubject.next(user))
    );
  }

  logout(): Observable<any> {
    return this.api.post('/auth/logout', {}).pipe(
      tap(() => this.currentUserSubject.next(null))
    );
  }

  checkAuth(): void {
    this.api.get<User>('/auth/me').subscribe({
      next: (user) => this.currentUserSubject.next(user),
      error: () => this.currentUserSubject.next(null)
    });
  }

  getCurrentUser(): User | null | undefined {
    return this.currentUserSubject.value;
  }

  isAuthenticated(): boolean {
    return this.currentUserSubject.value !== null;
  }

  isRole(role: string): boolean {
    const user = this.currentUserSubject.value;
    return user?.role === role;
  }
}
