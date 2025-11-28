import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InvestingComponent } from './investing.component';

describe('InvestingComponent', () => {
  let component: InvestingComponent;
  let fixture: ComponentFixture<InvestingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InvestingComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InvestingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
