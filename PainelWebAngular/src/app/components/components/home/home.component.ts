import { Component, OnInit, ViewChild } from '@angular/core';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartOptions, ChartType, Chart } from 'chart.js';
import DataLabelsPlugin from 'chartjs-plugin-datalabels';  // Importa o plugin de datalabels
import { UserService } from '../../services/user.service';
import { CategoryService } from '../../services/category.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
})
export class HomeComponent implements OnInit {
[x: string]: any;
  @ViewChild(BaseChartDirective) chart: BaseChartDirective | undefined;

  public chartUltimosUsuariosLogadosOptions: ChartOptions<'bar'> = {
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

  public chartUltimosUsuariosLogadosLabels: string[] = [];
  public chartUltimosUsuariosLogadosLegend = true;
  public chartUltimosUsuariosLogadosType = 'bar' as const;
  public chartUltimosUsuariosLogadosData: ChartConfiguration<'bar'>['data'] = {
    labels: this.chartUltimosUsuariosLogadosLabels,
    datasets: [{ data: [], label: 'Usuários Logados' }],
  };


  public chartCursosByCategoriaOptions: ChartOptions<'pie'> = {
    responsive: true,
    plugins: {
      legend: {
        display: true,
        position: 'top',
      },
      datalabels: {
        display: (context) => {
          return context.dataset.data[context.dataIndex] !== 0;
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

  public chartCursosByCategoriaLabels: string[] = [];
  public chartCursosByCategoriaLegend = true;
  public chartCursosByCategoriaType = 'pie' as const;
  public chartCursosByCategoriaData: ChartConfiguration<'pie'>['data'] = {
    labels: this.chartCursosByCategoriaLabels,
    datasets: [{
      data: [],
      backgroundColor: [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'
      ]
    }]
  };

  startDate: string;
  endDate: string;

  constructor(
    private userService: UserService,
    private categoryService: CategoryService
  ) {
    Chart.register(DataLabelsPlugin);

    Chart.defaults.set('plugins.datalabels', {
      display: (context : any) => context.dataset.data[context.dataIndex] !== 0,  // Oculta rótulos de valor zero
      color: '#fff',
      anchor: 'end',
      align: 'top'
    });

    const today = new Date();
    this.endDate = this.formatDate(today);

    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(today.getDate() - 7);
    this.startDate = this.formatDate(sevenDaysAgo);
  }

  ngOnInit(): void {
    this.loadUltimosUsuariosLogados();
    this.loadCategoriaUsuariosData();
  }

  formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  formatToDDMM(dateStr: string): string {
    const date = new Date(dateStr);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    return `${day}/${month}`;
  }

  loadUltimosUsuariosLogados(): void {
    this.userService
      .ultimosUsuariosLogados(this.startDate, this.endDate)
      .subscribe(
        (data) => {
          const updatedLabels = data.map((item: any) => this.formatToDDMM(item[0]));
          const updatedData = data.map((item: any) => item[1]);

          this.chartUltimosUsuariosLogadosLabels = [...updatedLabels];
          this.chartUltimosUsuariosLogadosData = {
            ...this.chartUltimosUsuariosLogadosData,
            datasets: [
              {
                ...this.chartUltimosUsuariosLogadosData.datasets[0],
                data: [...updatedData],
              },
            ],
          };

          if (this.chart) {
            this.chart.chart?.update();
          }
        },
        (error) => {
          console.error('Erro ao carregar usuários logados', error);
        }
      );
  }

  loadCategoriaUsuariosData(): void {
    this.categoryService.getDistribuicaoCursosAtivos(this.startDate, this.endDate).subscribe((data: any) => {

      this.chartCursosByCategoriaLabels = data.map((item: any) => item[1]);  // Nome da categoria
      this.chartCursosByCategoriaData.datasets[0].data = data.map((item: any) => item[2]);  // Total de usuários

      if (this.chart) {
        this.chart.update();
      }
    }, error => {
      console.error('Erro ao carregar os dados de categorias:', error);
    });
  }

  onChangeDate() {
    console.log("onChangeDate");
    this.loadUltimosUsuariosLogados();
    this.loadCategoriaUsuariosData();
  }
}
