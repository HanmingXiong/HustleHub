import { Routes } from '@angular/router';

// Import your new page components
import { HomeComponent } from './pages/home/home.component';
import { FinancialLiteracyComponent } from './pages/financial-literacy/financial-literacy.component';
import { CreditComponent } from './pages/credit/credit.component';
import { BudgetingComponent } from './pages/budgeting/budgeting.component';
import { InvestingComponent } from './pages/investing/investing.component';
import { ApplicantProfileComponent } from './pages/applicant-profile/applicant-profile.component';
import { EmployerProfileComponent } from './pages/employer-profile/employer-profile.component';
import { AuthComponent } from './pages/auth/auth.component';
import { CreateJobComponent } from './pages/create-job/create-job.component';
import { ApplyJobComponent } from './pages/apply-job/apply-job.component';
import { ApplicationsComponent } from './pages/applications/applications.component';
import { EmployerDashboardComponent } from './pages/employer-dashboard/employer-dashboard.component'

export const routes: Routes = [
    // Route for the Home page
    { 
        path: 'home', 
        component: HomeComponent 
    },

    {
        path: 'create-job',
        component: CreateJobComponent 
    },
    
    {
        path: 'apply/:id', 
        component: ApplyJobComponent
    },
    {
        path: 'applications',
        component: ApplicationsComponent
    },

    {
        path: 'employer/dashboard',
        component: EmployerDashboardComponent
    },

    {
        path: 'financial-literacy',
        component: FinancialLiteracyComponent
    },

    {
        path: 'financial-literacy/credit',
        component: CreditComponent
    },

    {
        path: 'financial-literacy/budgeting',
        component: BudgetingComponent
    },

    {
        path: 'financial-literacy/investing',
        component: InvestingComponent
    },

    {
        path: 'auth',
        component: AuthComponent
    },
    
    // Profile routes based on role
    { 
        path: 'profile/applicant', 
        component: ApplicantProfileComponent 
    },
    { 
        path: 'profile/employer', 
        component: EmployerProfileComponent 
    },
    { 
        path: 'profile/admin', 
        component: EmployerProfileComponent  // same as employer
    },
    // Redirect old profile route to home 
    { 
        path: 'profile', 
        redirectTo: 'home',
        pathMatch: 'full'
    },
    
    // Redirects base url to Home page
    { 
        path: '', 
        redirectTo: 'auth', 
        pathMatch: 'full' 
    },
    
    // will redirect non-existing route to home page
    { 
        path: '**', 
        redirectTo: 'home' 
    }
];
