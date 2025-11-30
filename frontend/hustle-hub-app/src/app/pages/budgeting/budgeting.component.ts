import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-budgeting',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './budgeting.component.html',
  styleUrl: './budgeting.component.css'
})
export class BudgetingComponent implements OnInit {
  resources: any[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.http.get<any[]>('http://localhost:8000/financial-literacy/budget')
      .subscribe(data => {
        this.resources = data;
      });
  }
}