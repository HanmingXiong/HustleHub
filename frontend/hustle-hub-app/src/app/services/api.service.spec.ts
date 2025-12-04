import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ApiService } from './api.service';

describe('ApiService', () => {
  let service: ApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ApiService]
    });
    service = TestBed.inject(ApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should make GET request', (done) => {
    const mockData = { id: 1, name: 'Test' };

    service.get('/test').subscribe(data => {
      expect(data).toEqual(mockData);
      done();
    });

    const req = httpMock.expectOne('http://localhost:8000/test');
    expect(req.request.method).toBe('GET');
    req.flush(mockData);
  });

  it('should make POST request', (done) => {
    const postData = { name: 'Test' };
    const mockResponse = { id: 1, name: 'Test' };

    service.post('/test', postData).subscribe(data => {
      expect(data).toEqual(mockResponse);
      done();
    });

    const req = httpMock.expectOne('http://localhost:8000/test');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(postData);
    req.flush(mockResponse);
  });

  it('should make PUT request', (done) => {
    const putData = { id: 1, name: 'Updated' };

    service.put('/test/1', putData).subscribe(data => {
      expect(data).toEqual(putData);
      done();
    });

    const req = httpMock.expectOne('http://localhost:8000/test/1');
    expect(req.request.method).toBe('PUT');
    req.flush(putData);
  });

  it('should make DELETE request', (done) => {
    service.delete('/test/1').subscribe(data => {
      expect(data).toBeTruthy();
      done();
    });

    const req = httpMock.expectOne('http://localhost:8000/test/1');
    expect(req.request.method).toBe('DELETE');
    req.flush({});
  });
});
