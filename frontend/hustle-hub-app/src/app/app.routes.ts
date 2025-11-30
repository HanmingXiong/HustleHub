import { Routes } from '@angular/router';

// Import your new page components
import { HomeComponent } from './pages/home/home.component';
import { AboutComponent } from './pages/about/about.component';
import { FinancialLiteracyComponent } from './pages/financial-literacy/financial-literacy.component';
import { CreditComponent } from './pages/credit/credit.component';
import { BudgetingComponent } from './pages/budgeting/budgeting.component';
import { InvestingComponent } from './pages/investing/investing.component';
import { ProfileComponent } from './pages/profile/profile.component';
import { AuthComponent } from './pages/auth/auth.component';

export const routes: Routes = [
    // Route for the Home page
    { 
        path: 'home', 
        component: HomeComponent 
    },
    
    // Route for the About page
    { 
        path: 'about', 
        component: AboutComponent 
    },

    {
        path: 'financial',
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
    
    // Route for the Profile page
    { 
        path: 'profile', 
        component: ProfileComponent 
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
