import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { map, take, filter } from 'rxjs/operators';

export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return authService.currentUser$.pipe(
    filter(user => user !== undefined),
    take(1),
    map(user => {
      if (user) {
        return true;
      }
      router.navigate(['/auth']);
      return false;
    })
  );
};

export const guestGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return authService.currentUser$.pipe(
    filter(user => user !== undefined),
    take(1),
    map(user => {
      if (!user) {
        return true;
      }
      router.navigate(['/home']);
      return false;
    })
  );
};
