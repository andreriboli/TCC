import { Injectable } from '@angular/core';
import { BaseService } from './base-service.service';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class VimeoService extends BaseService<any> {
    constructor(http: HttpClient) {
        super(http, 'vimeo');
    }

    getVideosMaisEngajados(): Observable<any> {
        let params = new HttpParams()

        return this.get('/mais-engajados', params);
    }

    getVideosComMelhorConclusao(): Observable<any> {
        let params = new HttpParams()

        return this.get('/melhor-conclusao', params);
    }
}
