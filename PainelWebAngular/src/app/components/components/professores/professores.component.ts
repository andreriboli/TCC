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

    @ViewChild(BaseChartDirective) chartTopProfessor: BaseChartDirective | undefined;
    @ViewChild(BaseChartDirective) chartProfessorMaisEngajado: BaseChartDirective | undefined;

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
                    return context.dataset.data[context.dataIndex] !== 0;
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
        datasets: [{
            data: [],
            label: 'Acessos',
            backgroundColor: [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'
            ],
            borderColor: '#333', // Opcional: cor da borda das barras
            borderWidth: 0.5 // Opcional: espessura da borda das barras
        }],
    };

    public chartProfessorMaisEngajadoOptions: ChartOptions<'bar'> = {
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
                    return context.dataset.data[context.dataIndex] !== 0;
                },
                color: '#fff',
                anchor: 'end',
                align: 'top'
            }
        }
    };

    public chartProfessorMaisEngajadoLabels: string[] = [];
    public chartProfessorMaisEngajadoLegend = false;
    public chartProfessorMaisEngajadoType = 'bar' as const;
    public chartProfessorMaisEngajadoData: ChartConfiguration<'bar'>['data'] = {
        labels: this.chartProfessorMaisEngajadoLabels,
        datasets: [{
            data: [],
            label: 'Acessos',
            backgroundColor: [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'
            ],
            borderColor: '#333', // Opcional: cor da borda das barras
            borderWidth: 0.5 // Opcional: espessura da borda das barras
        }],
    };


    constructor(private professorService: ProfessorService) { }

    ngOnInit(): void {
        Chart.register(ChartDataLabels);
        Chart.defaults.set('plugins.datalabels', {
            display: (context: any) => context.dataset.data[context.dataIndex] !== 0,  // Oculta rótulos de valor zero
            color: '#fff',
            anchor: 'end',
            align: 'top'
        });

        this.loadTopProfessores();
        this.loadProfessorMaisEngajado();

    }

    gerarCorAleatoria(): string {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }


    loadTopProfessores(): void {
        this.professorService.getTopProfessores().subscribe((data) => {
                const updatedLabels = data.map((item: any) => (item[0]));
                const updatedData = data.map((item: any) => item[1]);

                this.chartTopProfessorLabels = [...updatedLabels];
                this.chartTopProfessorData = {
                    ...this.chartTopProfessorData,
                    datasets: [
                        {
                            ...this.chartTopProfessorData.datasets[0],
                            data: [...updatedData],
                            label: 'Professores',
                        },
                    ],
                };

                if (this.chartTopProfessor) {
                    this.chartTopProfessor.chart?.update();
                }
            },(error) => {
                console.error('Erro ao carregar os dados dos top professores', error);
            }
        );
    }

    loadProfessorMaisEngajado(): void {
        this.professorService.getProfessorMaisEngajados().subscribe((data) => {
                const updatedLabels = data.map((item: any) => (item[0]));
                const updatedData = data.map((item: any) => item[3]);

                this.chartProfessorMaisEngajadoLabels = [...updatedLabels];
                this.chartProfessorMaisEngajadoData = {
                    ...this.chartProfessorMaisEngajadoData,
                    datasets: [
                        {
                            ...this.chartProfessorMaisEngajadoData.datasets[0],
                            data: [...updatedData],
                            label: 'Professores',
                        },
                    ],
                };

                if (this.chartProfessorMaisEngajado) {
                    this.chartProfessorMaisEngajado.chart?.update();
                }
            },(error) => {
                console.error('Erro ao carregar os dados dos top professores', error);
            }
        );
    }
}
