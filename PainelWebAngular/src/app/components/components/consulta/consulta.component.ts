import { Component } from '@angular/core';
import { BackendService } from '../../services/backend.service';

@Component({
  selector: 'app-consulta',
  templateUrl: './consulta.component.html',
  styleUrls: ['./consulta.component.scss']
})
export class ConsultaComponent {
  parametro1: string = '';
  parametro2: string = '';
  resultado: string = '';

  constructor(private backendService: BackendService) { }

  enviarConsulta(): void {
    this.backendService.consultar(this.parametro1, this.parametro2)
      .subscribe(response => {
        this.resultado = response.resultado;
      }, error => {
        console.error('Erro ao consultar o backend', error);
      });
  }
}
