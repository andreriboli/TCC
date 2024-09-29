import { BaseService } from './base-service.service';
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

export class UserService extends BaseService<any> {

  constructor(http: HttpClient) {
    super(http, 'usuarios');  // Define o caminho base do recurso /usuarios
  }

  ultimosUsuariosLogados(startDate: string, endDate: string): Observable<any> {
    let params = new HttpParams()
      .set('startDate', startDate)
      .set('endDate', endDate);

    return this.get('/logados', params);
  }

  // Outros métodos como getAllUsers, getUserById, etc.
}
