import { Routes } from '@angular/router';

// Import your new page components
import { HomeComponent } from './pages/home/home.component';
import { AboutComponent } from './pages/about/about.component';

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
    
    // Redirects base url to Home page
    { 
        path: '', 
        redirectTo: 'home', 
        pathMatch: 'full' 
    },
    
    // will redirect non-existing route to home page
    { 
        path: '**', 
        redirectTo: 'home' 
    }
];