import { Injectable } from '@angular/core';
import { BaseService } from './base-service.service';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class CategoryService extends BaseService<any> {
  constructor(http: HttpClient) {
    super(http, 'categorias');
  }

  getDistribuicaoCursosAtivos(startDate: string, endDate: string): Observable<any> {
    let params = new HttpParams()
        .set('startDate', startDate)
        .set('endDate', endDate);

    return this.get('/distribuicao-cursos-ativos', params);
  }
}
