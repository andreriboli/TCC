import { Injectable } from '@angular/core';
import { BaseService } from './base-service.service';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ProfessorService extends BaseService<any> {
  constructor(http: HttpClient) {
    super(http, 'professor');
  }

  getTopProfessores(): Observable<any> {
    let params = new HttpParams()

    return this.get('/top-professor', params);
  }
}

