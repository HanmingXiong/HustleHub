import { ApplicationConfig, provideZoneChangeDetection, importProvidersFrom } from '@angular/core';
import { provideClientHydration, withEventReplay } from '@angular/platform-browser';
import { provideHttpClient, withFetch } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    // Core platform providers: hydration, HTTP, forms, routing
    provideZoneChangeDetection({ eventCoalescing: true }), 
    provideClientHydration(withEventReplay()),
    provideHttpClient(
      withFetch(),    
    ),
    importProvidersFrom(FormsModule),
    provideRouter(routes) 
  ]
};
