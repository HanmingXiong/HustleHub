import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-financial-literacy',
  standalone: true, 
  imports: [FormsModule, CommonModule, HttpClientModule],
  templateUrl: './financial-literacy.component.html',
  styleUrls: ['./financial-literacy.component.css']
})
export class FinancialLiteracyComponent {
  website = '';
  resource_type: 'budget' | 'credit' | 'invest' = 'budget';
  message = '';
  isAdmin = false;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.http.get('http://localhost:8000/auth/me', { withCredentials: true })
      .subscribe({
        next: (user: any) => this.isAdmin = user.role === 'admin',
        error: () => this.isAdmin = false
      });
  }

  createResource() {
    if (!this.website || !this.resource_type) {
      this.message = 'Website and type are required';
      return;
    }

    const body = { website: this.website, resource_type: this.resource_type };
    this.http.post('http://localhost:8000/financial-literacy', body, { withCredentials: true })
      .subscribe({
        next: () => {
          this.message = 'Resource created successfully!';
          this.website = '';
          this.resource_type = 'budget';
        },
        error: err => this.message = 'Error: ' + (err.error?.detail || 'Unknown error')
      });
  }
}
