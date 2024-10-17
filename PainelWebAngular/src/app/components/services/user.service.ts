import { BaseService } from './base-service.service';
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})

export class UserService extends BaseService<any> {

    constructor(http: HttpClient) {
        super(http, 'usuarios');
    }

    getUltimosUsuariosLogados(startDate: string, endDate: string): Observable<any> {
        let params = new HttpParams()
            .set('startDate', startDate)
            .set('endDate', endDate);

        return this.get('/logados', params);
    }

    getAlunosMenosEngajados(startDate: string, endDate: string): Observable<any> {
        let params = new HttpParams()
            .set('startDate', startDate)
            .set('endDate', endDate);

        return this.get('/menos-engajados', params);
    }

    getAlunosMaisEngajados(startDate: string, endDate: string): Observable<any> {
        let params = new HttpParams()
            .set('startDate', startDate)
            .set('endDate', endDate);

        return this.get('/mais-engajados', params);
    }

    getAlunosSemCertificado(): Observable<any> {
        let params = new HttpParams();

        return this.get('/sem-certificado', params);
    }


}
