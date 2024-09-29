import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export abstract class BaseService<T> {

  private apiUrl = 'http://localhost:5000/api';  // URL base da API

  constructor(protected http: HttpClient, protected resourcePath: string) {}

  get(path: string, params?: HttpParams): Observable<T> {
    return this.http.get<T>(`${this.apiUrl}/${this.resourcePath}${path}`, { params });
  }

  post(path: string, body: any, headers?: HttpHeaders): Observable<T> {
    return this.http.post<T>(`${this.apiUrl}/${this.resourcePath}${path}`, body, { headers });
  }

  put(path: string, body: any, headers?: HttpHeaders): Observable<T> {
    return this.http.put<T>(`${this.apiUrl}/${this.resourcePath}${path}`, body, { headers });
  }

  delete(path: string, params?: HttpParams): Observable<T> {
    return this.http.delete<T>(`${this.apiUrl}/${this.resourcePath}${path}`, { params });
  }

}
