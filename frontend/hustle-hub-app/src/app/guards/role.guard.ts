import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { map, take, filter } from 'rxjs/operators';

export const roleGuard: CanActivateFn = (route) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const expectedRole = route.data['role'] as string | string[];

  return authService.currentUser$.pipe(
    filter(user => user !== undefined),
    take(1),
    map(user => {
      if (!user) {
        router.navigate(['/auth']);
        return false;
      }

      // Admins have full access to all routes
      if (user.role === 'admin') {
        return true;
      }

      // Handle multiple allowed roles
      const allowedRoles = Array.isArray(expectedRole) ? expectedRole : [expectedRole];

      // Allow access if user has one of the correct roles
      if (allowedRoles.includes(user.role)) {
        return true;
      }

      // Redirect to their own profile type if trying to access wrong profile
      router.navigate([`/profile/${user.role}`]);
      return false;
    })
  );
};
