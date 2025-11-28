import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FinancialLiteracyComponent } from './financial-literacy.component';

describe('FinancialLiteracyComponent', () => {
  let component: FinancialLiteracyComponent;
  let fixture: ComponentFixture<FinancialLiteracyComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FinancialLiteracyComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FinancialLiteracyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
