import { Component, OnInit, ViewChild } from '@angular/core';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartOptions, ChartType } from 'chart.js';
import { UserService } from '../../services/user-service.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
})
export class HomeComponent implements OnInit {
  @ViewChild(BaseChartDirective) chart: BaseChartDirective | undefined; // Acessa o gráfico

  public barChartUltimosUsuariosLogadosOptions: ChartOptions<'bar'> = {
    responsive: true,
    scales: {
      y: {
        ticks: {
          stepSize: 1,
        },
      },
    },
  };

  public barChartUltimosUsuariosLogadosLabels: string[] = [];
  public barChartUltimosUsuariosLogadosLegend = true;
  public barChartUltimosUsuariosLogadosType = 'bar' as const;

  public barChartUltimosUsuariosLogadosData: ChartConfiguration<'bar'>['data'] =
    {
      labels: this.barChartUltimosUsuariosLogadosLabels,
      datasets: [{ data: [], label: 'Usuários Logados' }],
    };

  startDate: string;
  endDate: string;

  constructor(private userService: UserService) {
    const today = new Date();
    this.endDate = this.formatDate(today);

    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(today.getDate() - 30);
    this.startDate = this.formatDate(sevenDaysAgo);
  }

  ngOnInit(): void {
    this.loadUltimosUsuariosLogados();
  }

  formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Mês precisa de +1
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  formatToDDMM(dateStr: string): string {
    const date = new Date(dateStr);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Mês em JS é zero-indexado
    return `${day}/${month}`;
  }

  loadUltimosUsuariosLogados(): void {
    this.userService
      .ultimosUsuariosLogados(this.startDate, this.endDate)
      .subscribe(
        (data) => {
          console.log('Dados recebidos da API:', data);

          // Atualizando as labels e os dados
          const updatedLabels = data.map((item: any) => {
            console.log('Data antes de formatar:', item[0]); // Verificar o formato original
            const formattedDate = this.formatToDDMM(item[0]);
            console.log('Data formatada:', formattedDate); // Verificar a data formatada
            return formattedDate;
          });

          const updatedData = data.map((item: any) => {
            console.log('Quantidade de logins:', item[1]); // Verificar os dados de loginCount
            return item[1];
          });

          // Clonando os arrays para garantir a detecção de mudança
          this.barChartUltimosUsuariosLogadosLabels = [...updatedLabels];
          this.barChartUltimosUsuariosLogadosData = {
            ...this.barChartUltimosUsuariosLogadosData,
            datasets: [
              {
                ...this.barChartUltimosUsuariosLogadosData.datasets[0],
                data: [...updatedData],
              },
            ],
          };

          console.log(
            'Labels finais:',
            this.barChartUltimosUsuariosLogadosLabels
          );
          console.log('Dados finais:', this.barChartUltimosUsuariosLogadosData);

          // Chamar o update() para renderizar o gráfico novamente
          console.log(this.chart);
          if (this.chart) {
            this.chart.chart?.update();
          }
        },
        (error) => {
          console.error('Erro ao carregar usuários logados', error);
        }
      );
  }
}
