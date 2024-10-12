import { Component, OnInit, AfterViewInit, ViewChild } from '@angular/core';
import { Chart, ChartConfiguration, ChartOptions, ChartType } from 'chart.js';
import { CursosService } from '../../services/cursos.service';
import { BaseChartDirective } from 'ng2-charts';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { ChartEvent } from 'chart.js/dist/core/core.plugins';

@Component({
    selector: 'app-cursos',
    templateUrl: './cursos.component.html',
    styleUrls: ['./cursos.component.scss'],
})
export class CursosComponent implements OnInit, AfterViewInit {
    @ViewChild(BaseChartDirective) chartDistribuicao: | BaseChartDirective | undefined;
    @ViewChild(BaseChartDirective) chartTopCursos: | BaseChartDirective | undefined;
    @ViewChild(BaseChartDirective) chartCursoMenosInscricoes : | BaseChartDirective | undefined;

    public chartDistribuicaoCursosAtivosLabels: string[] = [];
    public chartDistribuicaoCursosAtivosData: number[] = [];

    public chartDistribuicaoCursosAtivosOptions: ChartOptions<'pie'> = {
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
                    size: 16,
                },
                anchor: 'center',
                align: 'center',
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        const label = context.label || '';
                        const value = context.raw || 0;
                        return `${label}: ${value}`;
                    },
                },
            },
        },
    };

    public chartDistribuicaoCursosAtivosType = 'pie' as const;
    public chartDistribuicaoCursosAtivosDataConfig: ChartConfiguration<'pie'>['data'] =
        {
            labels: this.chartDistribuicaoCursosAtivosLabels,
            datasets: [
                {
                    data: this.chartDistribuicaoCursosAtivosData,
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF',
                        '#FF9F40',
                        '#C9CBCF',
                    ],
                },
            ],
        };

    public chartCursoMenosInscricoesLabels: string[] = [];
    public chartCursoMenosInscricoesData: number[] = [];

    public chartCursoMenosInscricoesOptions: ChartOptions<'pie'> = {
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
                    size: 16,
                },
                anchor: 'center',
                align: 'center',
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        const label = context.label || '';
                        const value = context.raw || 0;
                        return `${label}: ${value}`;
                    },
                },
            },
        },
    };

    public chartCursoMenosInscricoesType = 'pie' as const;
    public chartCursoMenosInscricoesDataConfig: ChartConfiguration<'pie'>['data'] =
        {
            labels: this.chartCursoMenosInscricoesLabels,
            datasets: [
                {
                    data: this.chartCursoMenosInscricoesData,
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF',
                        '#FF9F40',
                        '#C9CBCF',
                    ],
                },
            ],
        };

    @ViewChild(BaseChartDirective) chartTopCursoSemana:
        | BaseChartDirective
        | undefined;

    public chartTopCursoSemanaOptions: ChartOptions<'bar'> = {
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

    public chartTopCursoSemanaLabels: string[] = [];
    public chartTopCursoSemanaLegend = false;
    public chartTopCursoSemanaType = 'bar' as const;
    public chartTopCursoSemanaData: ChartConfiguration<'bar'>['data'] = {
        labels: this.chartTopCursoSemanaLabels,
        datasets: [{ data: [], label: 'Acessos' }],
    };

    private originalData: number[] = [];
    constructor(private cursosService: CursosService) { }

    ngOnInit(): void {
        Chart.register(ChartDataLabels);
        Chart.defaults.set('plugins.datalabels', {
            display: (context: any) => context.dataset.data[context.dataIndex] !== 0, // Oculta rótulos de valor zero
            color: '#fff',
            anchor: 'end',
            align: 'top',
        });

        this.loadDistribuicaoCursosAtivosData();
        this.loadTopCursosSemana();
        this.loadCursosMenosInscricoes();
    }

    loadTopCursosSemana(): void {
        this.cursosService
            .getTopCursosMaisAcessadosSemana()
            .subscribe(
                (data) => {
                    const updatedLabels = data.map((item: any) => (item[1]));  // Assumindo que o nome do curso está no índice 1
                    const updatedData = data.map((item: any) => item[2]);  // Assumindo que os acessos estão no índice 2

                    this.chartTopCursoSemanaLabels = [...updatedLabels];
                    this.chartTopCursoSemanaData = {
                        ...this.chartTopCursoSemanaData,
                        datasets: [
                            {
                                ...this.chartTopCursoSemanaData.datasets[0],  // Acessando o primeiro conjunto de dados
                                data: [...updatedData],
                                label: 'Acessos',  // Adiciona o rótulo apropriado para a legenda
                            },
                        ],
                    };

                    if (this.chartTopCursos) {
                        this.chartTopCursos.chart?.update();
                    }
                },
                (error) => {
                    console.error('Erro ao carregar os dados dos cursos mais acessados', error);
                }
            );
    }

    loadCursosMenosInscricoes(): void {
        this.cursosService.getCursosMenosInscricoes().subscribe(
            (data) => {
                const updatedLabels = data.map((item: any) => item[1]); // Assumindo que o nome do curso está no índice 1
                const updatedData = data.map((item: any) => item[2]); // Assumindo que os acessos estão no índice 2

                this.chartTopCursoSemanaLabels = [...updatedLabels];
                this.chartTopCursoSemanaData = {
                    ...this.chartTopCursoSemanaData,
                    datasets: [
                        {
                            ...this.chartTopCursoSemanaData.datasets[0], // Acessando o primeiro conjunto de dados
                            data: [...updatedData],
                            label: 'Acessos', // Adiciona o rótulo apropriado para a legenda
                        },
                    ],
                };

                if (this.chartTopCursoSemana) {
                    this.chartTopCursoSemana.chart?.update();
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

    ngAfterViewInit(): void {
        // this.ajustaGraficoCursosAtivos();
    }

    ajustaGraficoCursosAtivos(): void {
        // setTimeout(() => {
        //   if (this.chartDistribuicao && this.chartDistribuicao.chart) {
        //     const legendBox = this.chartDistribuicao.chart.boxes[0] as any;
        //     console.log('Legend Items after render: ', legendBox?.legendItems);
        //     this.originalData = [
        //       ...(this.chartDistribuicao.chart.data.datasets[0].data as number[]),
        //     ];
        //     if (legendBox?.legendItems && legendBox.legendItems.length > 5) {
        //       const datasets = this.chartDistribuicao.chart.data.datasets[0];
        //       if (datasets && datasets.data) {
        //         for (let i = 5; i < datasets.data.length; i++) {
        //           datasets.data[i] = 0;
        //           const metaElement = this.chartDistribuicao!.chart!.getDatasetMeta(
        //             0
        //           ).data[i] as any;
        //           metaElement.hidden = true;
        //         }
        //       }
        //       this.chartDistribuicao.chart.update();
        //     }
        //     if (
        //       this.chartDistribuicao.chart.config.options &&
        //       this.chartDistribuicao.chart.config.options.plugins
        //     ) {
        //       this.chartDistribuicao.chart.config.options.plugins.legend!.onClick =
        //         (e: ChartEvent, legendItem: any) => {
        //           const index = legendItem.index;
        //           const datasets = this.chartDistribuicao!.chart?.data.datasets[0];
        //           const meta = this.chartDistribuicao!.chart?.getDatasetMeta(0);
        //           if (datasets?.data) {
        //             if (datasets.data[index] === 0) {
        //               const metaElement = meta!.data[index] as any;
        //               metaElement.hidden = false;
        //               (meta!.data[index] as any).hidden = false;
        //             } else {
        //               const metaElement = meta!.data[index] as any;
        //               metaElement.hidden = true;
        //               datasets.data[index] = 0;
        //               (meta!.data[index] as any).hidden = true;
        //             }
        //             this.chartDistribuicao!.chart?.update();
        //           }
        //         };
        //     }
        //   }
        // }, 400);
    }

    loadDistribuicaoCursosAtivosData(): void {
        this.cursosService.getDistribuicaoAlunosPorCurso().subscribe(
            (data: any) => {
                this.chartDistribuicaoCursosAtivosLabels = data.map(
                    (curso: any) => curso.nome_curso
                );
                this.chartDistribuicaoCursosAtivosData = data.map(
                    (curso: any) => curso.total_alunos
                );

                this.chartDistribuicaoCursosAtivosDataConfig = {
                    labels: [...this.chartDistribuicaoCursosAtivosLabels],
                    datasets: [
                        {
                            data: [...this.chartDistribuicaoCursosAtivosData],
                            backgroundColor: [
                                '#FF6384',
                                '#36A2EB',
                                '#FFCE56',
                                '#4BC0C0',
                                '#9966FF',
                                '#FF9F40',
                                '#C9CBCF',
                            ],
                        },
                    ],
                };

                if (this.chartDistribuicao) {
                    this.chartDistribuicao.update();
                }
            },
            (error) => {
                console.error('Erro ao carregar os dados dos cursos:', error);
            }
        );
    }
}
