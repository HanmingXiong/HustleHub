import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-investing',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './investing.component.html',
  styleUrl: './investing.component.css'
})
export class InvestingComponent implements OnInit {
  resources: any[] = [];
  isAdmin = false;
  isAuthenticated = false;
  editingResource: any = null;
  showDeleteModal = false;
  resourceToDelete: { id: number, name: string } | null = null;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.checkAuth();
    this.loadResources();
  }

  checkAuth() {
    this.http.get('http://localhost:8000/auth/me', { withCredentials: true })
      .subscribe({
        next: (user: any) => {
          this.isAuthenticated = true;
          this.isAdmin = user.role === 'admin';
        },
        error: () => {
          this.isAuthenticated = false;
          this.isAdmin = false;
        }
      });
  }

  loadResources() {
    this.http.get<any[]>('http://localhost:8000/financial-literacy/invest', { withCredentials: true })
      .subscribe(data => {
        this.resources = data;
      });
  }

  likeResource(resourceId: number) {
    this.http.post(`http://localhost:8000/financial-literacy/${resourceId}/like`, {}, { withCredentials: true })
      .subscribe({
        next: () => this.loadResources(),
        error: (err) => {
          // If already liked (400 error), unlike it instead
          if (err.status === 400) {
            this.http.delete(`http://localhost:8000/financial-literacy/${resourceId}/like`, { withCredentials: true })
              .subscribe({
                next: () => this.loadResources(),
                error: (unlikeErr) => console.error('Error unliking resource:', unlikeErr)
              });
          } else {
            console.error('Error liking resource:', err);
          }
        }
      });
  }

  editResource(resource: any) {
    this.editingResource = { ...resource };
  }

  saveEdit() {
    if (!this.editingResource) return;

    const body = {
      name: this.editingResource.name,
      website: this.editingResource.website,
      description: this.editingResource.description,
      resource_type: this.editingResource.resource_type
    };

    this.http.put(`http://localhost:8000/financial-literacy/${this.editingResource.resource_id}`, body, { withCredentials: true })
      .subscribe({
        next: () => {
          this.editingResource = null;
          this.loadResources();
        },
        error: (err) => console.error('Error updating resource:', err)
      });
  }

  cancelEdit() {
    this.editingResource = null;
  }

  deleteResource(resourceId: number, resourceName: string) {
    this.resourceToDelete = { id: resourceId, name: resourceName };
    this.showDeleteModal = true;
  }

  confirmDelete() {
    if (!this.resourceToDelete) return;

    this.http.delete(`http://localhost:8000/financial-literacy/${this.resourceToDelete.id}`, { withCredentials: true })
      .subscribe({
        next: () => {
          this.loadResources();
          this.closeDeleteModal();
        },
        error: (err) => console.error('Error deleting resource:', err)
      });
  }

  closeDeleteModal() {
    this.showDeleteModal = false;
    this.resourceToDelete = null;
  }
}