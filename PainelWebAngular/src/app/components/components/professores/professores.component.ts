import { Component, OnInit, AfterViewInit, ViewChild } from '@angular/core';
import { Chart, ChartConfiguration, ChartOptions, ChartType } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { ProfessorService } from '../../services/professor.service';

@Component({
  selector: 'app-professores',
  templateUrl: './professores.component.html',
  styleUrls: ['./professores.component.scss']
})
export class ProfessoresComponent implements OnInit {

  @ViewChild(BaseChartDirective) chart: BaseChartDirective | undefined;

  public chartTopProfessorOptions: ChartOptions<'bar'> = {
    responsive: true,
    scales: {
      y: {
        ticks: {
          stepSize: 1,
        },
      },
    },
    plugins: {
      datalabels: {
        display: (context) => {
          return context.dataset.data[context.dataIndex] !== 0;  // Oculta rótulos com valor zero
        },
        color: '#fff',
        anchor: 'end',
        align: 'top'
      }
    }
  };

  public chartTopProfessorLabels: string[] = [];
  public chartTopProfessorLegend = false;
  public chartTopProfessorType = 'bar' as const;
  public chartTopProfessorData: ChartConfiguration<'bar'>['data'] = {
    labels: this.chartTopProfessorLabels,
    datasets: [{ data: [], label: 'Acessos' }],
  };


  constructor(private professorService: ProfessorService) {}

  ngOnInit(): void {
    Chart.register(ChartDataLabels);
    Chart.defaults.set('plugins.datalabels', {
        display: (context : any) => context.dataset.data[context.dataIndex] !== 0,  // Oculta rótulos de valor zero
        color: '#fff',
        anchor: 'end',
        align: 'top'
    });

    this.loadTopProfessores();

  }

  loadTopProfessores(): void {
    this.professorService
      .getTopProfessores()
      .subscribe(
        (data) => {
          const updatedLabels = data.map((item: any) => (item[0]));  // Assumindo que o nome do curso está no índice 1
          const updatedData = data.map((item: any) => item[1]);  // Assumindo que os acessos estão no índice 2

          this.chartTopProfessorLabels = [...updatedLabels];
          this.chartTopProfessorData = {
            ...this.chartTopProfessorData,
            datasets: [
              {
                ...this.chartTopProfessorData.datasets[0],  // Acessando o primeiro conjunto de dados
                data: [...updatedData],
                label: 'Professores',  // Adiciona o rótulo apropriado para a legenda
              },
            ],
          };

          if (this.chart) {
            this.chart.chart?.update();
          }
        },
        (error) => {
          console.error('Erro ao carregar os dados dos top professores', error);
        }
      );
  }

}
