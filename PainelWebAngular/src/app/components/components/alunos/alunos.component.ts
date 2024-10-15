import { Component, OnInit, AfterViewInit, ViewChild } from '@angular/core';
import { Chart, ChartConfiguration, ChartOptions, ChartType } from 'chart.js';
import { CursosService } from '../../services/cursos.service';
import { BaseChartDirective } from 'ng2-charts';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { ChartEvent } from 'chart.js/dist/core/core.plugins';
import { UserService } from '../../services/user.service';

@Component({
    selector: 'app-alunos',
    templateUrl: './alunos.component.html',
    styleUrls: ['./alunos.component.scss'],
})
export class AlunosComponent implements OnInit {

    @ViewChild(BaseChartDirective) chartAlunosMenosEngajados: | BaseChartDirective | undefined;
    public chartAlunosMenosEngajadosOptions: ChartOptions<'bar'> = {
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
                    return context.dataset.data[context.dataIndex] !== 0; // Oculta rótulos com valor zero
                },
                color: '#fff',
                anchor: 'end',
                align: 'top',
            },
        },
    };
    public chartAlunosMenosEngajadosLabels: string[] = [];
    public chartAlunosMenosEngajadosLegend = false;
    public chartAlunosMenosEngajadosType = 'bar' as const;
    public chartAlunosMenosEngajadosData: ChartConfiguration<'bar'>['data'] = {
        labels: this.chartAlunosMenosEngajadosLabels,
        datasets: [{ data: [], label: 'Acessos' }],
    };

    @ViewChild(BaseChartDirective) chartAlunosMaisEngajados: | BaseChartDirective | undefined;
    public chartAlunosMaisEngajadosOptions: ChartOptions<'bar'> = {
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
                    return context.dataset.data[context.dataIndex] !== 0; // Oculta rótulos com valor zero
                },
                color: '#fff',
                anchor: 'end',
                align: 'top',
            },
        },
    };
    public chartAlunosMaisEngajadosLabels: string[] = [];
    public chartAlunosMaisEngajadosLegend = false;
    public chartAlunosMaisEngajadosType = 'bar' as const;
    public chartAlunosMaisEngajadosData: ChartConfiguration<'bar'>['data'] = {
        labels: this.chartAlunosMaisEngajadosLabels,
        datasets: [{ data: [], label: 'Acessos' }],
    };

    private originalData: number[] = [];
    constructor(private userService: UserService) { }

    startDate: string | undefined;
    endDate: string | undefined;

    ngOnInit(): void {
        Chart.register(ChartDataLabels);
        Chart.defaults.set('plugins.datalabels', {
            display: (context: any) => context.dataset.data[context.dataIndex] !== 0, // Oculta rótulos de valor zero
            color: '#fff',
            anchor: 'end',
            align: 'top',
        });

        this.ajustaData();
        this.loadAlunosMenosEngajados();
        this.loadAlunosMaisEngajados();
    }

    ajustaData() {
      const today = new Date();
      this.endDate = this.formatDate(today);

      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(today.getDate() - 30);
      this.startDate = this.formatDate(sevenDaysAgo);
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

    loadAlunosMenosEngajados(): void {
        this.userService.getAlunosMenosEngajados(this.startDate!, this.endDate!).subscribe(
            (data) => {
                const updatedLabels = data.map((item: any) => item[0]); // Assumindo que o nome do curso está no índice 1
                const updatedData = data.map((item: any) => item[1]); // Assumindo que os acessos estão no índice 2

                this.chartAlunosMenosEngajadosLabels = [...updatedLabels];
                this.chartAlunosMenosEngajadosData = {
                    ...this.chartAlunosMenosEngajadosData,
                    datasets: [
                        {
                            ...this.chartAlunosMenosEngajadosData.datasets[0], // Acessando o primeiro conjunto de dados
                            data: [...updatedData],
                            label: 'Acessos', // Adiciona o rótulo apropriado para a legenda
                        },
                    ],
                };

                if (this.chartAlunosMenosEngajados) {
                    this.chartAlunosMenosEngajados.chart?.update();
                }
            },
            (error) => {
                console.error(
                    'Erro ao carregar os dados dos cursos mais acessados',
                    error
                );
            }
        );
    }

    loadAlunosMaisEngajados(): void {
        this.userService.getAlunosMaisEngajados(this.startDate!, this.endDate!).subscribe(
            (data) => {
                const updatedLabels = data.map((item: any) => item[0]); // Assumindo que o nome do curso está no índice 1
                const updatedData = data.map((item: any) => item[1]); // Assumindo que os acessos estão no índice 2

                this.chartAlunosMaisEngajadosLabels = [...updatedLabels];
                this.chartAlunosMaisEngajadosData = {
                    ...this.chartAlunosMaisEngajadosData,
                    datasets: [
                        {
                            ...this.chartAlunosMaisEngajadosData.datasets[0], // Acessando o primeiro conjunto de dados
                            data: [...updatedData],
                            label: 'Acessos', // Adiciona o rótulo apropriado para a legenda
                        },
                    ],
                };
            },
            (error) => {
                console.error(
                    'Erro ao carregar os dados dos cursos mais acessados',
                    error
                );
            }
        );
    }

    onChangeDate() {
        this.loadAlunosMenosEngajados();
    }
}
