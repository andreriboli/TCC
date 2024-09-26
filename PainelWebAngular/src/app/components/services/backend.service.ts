import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class BackendService {

  private apiUrl = 'http://localhost:5000/api/consulta';  // URL do backend

  constructor(private http: HttpClient) { }

  consultar(parametro1: string, parametro2: string): Observable<any> {
    let params = new HttpParams()
      .set('parametro1', parametro1)
      .set('parametro2', parametro2);

    return this.http.get(this.apiUrl, { params });
  }
}
