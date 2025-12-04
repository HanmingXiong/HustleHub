import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AuthService, User, RegisterData, LoginData } from './auth.service';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AuthService]
    });
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
    
    // Handle the initial checkAuth call
    const authReq = httpMock.match('http://localhost:8000/auth/me');
    authReq.forEach(req => req.flush(null, { status: 401, statusText: 'Unauthorized' }));
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should register a user', (done) => {
    const registerData: RegisterData = {
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123',
      role: 'applicant'
    };

    const mockUser: User = {
      user_id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'applicant'
    };

    service.register(registerData).subscribe(response => {
      expect(response).toEqual(mockUser);
      expect(service.getCurrentUser()).toEqual(mockUser);
      done();
    });

    const req = httpMock.expectOne('http://localhost:8000/auth/register');
    expect(req.request.method).toBe('POST');
    req.flush(mockUser);
  });

  it('should login a user', (done) => {
    const loginData: LoginData = {
      email: 'test@example.com',
      password: 'password123'
    };

    const mockUser: User = {
      user_id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'applicant'
    };

    service.login(loginData).subscribe(response => {
      expect(response).toEqual(mockUser);
      expect(service.getCurrentUser()).toEqual(mockUser);
      done();
    });

    const req = httpMock.expectOne('http://localhost:8000/auth/login');
    expect(req.request.method).toBe('POST');
    req.flush(mockUser);
  });

  it('should logout a user', (done) => {
    service.logout().subscribe(() => {
      expect(service.getCurrentUser()).toBeNull();
      done();
    });

    const req = httpMock.expectOne('http://localhost:8000/auth/logout');
    expect(req.request.method).toBe('POST');
    req.flush({});
  });

  it('should check if user is authenticated', () => {
    expect(service.isAuthenticated()).toBeFalse();
  });

  it('should check user role', () => {
    expect(service.isRole('applicant')).toBeFalse();
  });
});
