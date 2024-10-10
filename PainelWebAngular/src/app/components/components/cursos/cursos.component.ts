import { Component, OnInit } from '@angular/core';
import { ChartConfiguration, ChartOptions, ChartType } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';  // Import do plugin
import { CursosService } from '../../services/cursos.service';
import { Chart } from 'chart.js';

@Component({
  selector: 'app-cursos',
  templateUrl: './cursos.component.html',
  styleUrls: ['./cursos.component.scss']
})
export class CursosComponent implements OnInit {

  public chartDistribuicaoCursosAtivosLabels: string[] = [];
  public chartDistribuicaoCursosAtivosData: number[] = [];

  public chartDistribuicaoCursosAtivosOptions: ChartOptions<'pie'> = {
    responsive: true,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        // Aqui controlamos a visibilidade das legendas
        labels: {
          generateLabels: (chart) => {
            const originalLabels = chart.data.labels || [];
            return originalLabels.map((label: any, index: number) => ({
              text: label,
              // fillStyle: chart.data.datasets[0].backgroundColor[index],
              hidden: index >= 5 // Oculta acima do índice 4
            }));
          }
        }
      },
      // Datalabels plugin para mostrar valores dentro das fatias
      datalabels: {
        display: (context) => {
          return context.dataset.data[context.dataIndex] !== 0;  // Mostrar somente se o valor for diferente de 0
        },
        color: '#fff',
        font: {
          weight: 'bold',
          size: 16
        },
        anchor: 'center',
        align: 'center'
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.raw || 0;
            return `${label}: ${value}`;
          }
        }
      }
    }
  };

  public chartDistribuicaoCursosAtivosType = 'pie' as const;
  public chartDistribuicaoCursosAtivosDataConfig: ChartConfiguration<'pie'>['data'] = {
    labels: this.chartDistribuicaoCursosAtivosLabels,
    datasets: [{
      data: this.chartDistribuicaoCursosAtivosData,
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'],
      // Não usamos hidden aqui
    }]
  };

  constructor(private cursosService: CursosService) {}

  ngOnInit(): void {
    // Registrar o plugin ChartDataLabels
    Chart.register(ChartDataLabels);

    this.loadDistribuicaoCursosAtivosData();
  }

  loadDistribuicaoCursosAtivosData(): void {
    this.cursosService.getDistribuicaoAlunosPorCurso().subscribe((data: any) => {
      // Atualiza os dados do gráfico com os valores recebidos da API
      this.chartDistribuicaoCursosAtivosLabels = data.map((curso: any) => curso.nome_curso);
      this.chartDistribuicaoCursosAtivosData = data.map((curso: any) => curso.total_alunos);

      // Configura o gráfico com os novos valores
      this.chartDistribuicaoCursosAtivosDataConfig = {
        labels: [...this.chartDistribuicaoCursosAtivosLabels],
        datasets: [{
          data: [...this.chartDistribuicaoCursosAtivosData],
          backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF']
        }]
      };
    }, error => {
      console.error('Erro ao carregar os dados dos cursos:', error);
    });
  }
}
