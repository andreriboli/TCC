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
    @ViewChild(BaseChartDirective) chartAlunosMaisEngajados: | BaseChartDirective | undefined;

    barChart:  Chart | undefined;
    chartAlunosSemCertificado:  Chart | undefined;

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
                    return context.dataset.data[context.dataIndex] !== 0;
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
        datasets: [{ data: [],
            backgroundColor: [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'
            ],
            label: 'Acessos'
        }],
    };

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
                    return context.dataset.data[context.dataIndex] !== 0;
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
        datasets: [{ data: [],
            backgroundColor: [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'
            ],
            label: 'Acessos'
        }],
    };


    public chartAlunosSemCertificadoOptions: ChartOptions<'bar'> = {
        responsive: true,
        plugins: {
            datalabels: {
                display: (context) => {
                    return context.dataset.data[context.dataIndex] !== 0;
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    font: {
                        size: 11,
                    },
                    autoSkip: false,
                    maxRotation: 45,
                    minRotation: 15,
                },
            },
            y: {
                ticks: {
                    font: {
                        size: 11,
                    },
                    stepSize: 3,
                },
            },
        },
    };
    public chartAlunosSemCertificadoLabels: string[] = [];
    public chartAlunosSemCertificadoLegend = false;
    public chartAlunosSemCertificadoType = 'bar' as const;
    public chartAlunosSemCertificadoData: ChartConfiguration<'bar'>['data'] = {
        labels: this.chartAlunosSemCertificadoLabels,
        datasets: [{
            data: [], // Os dados serão atualizados dinamicamente
            backgroundColor: this.chartAlunosSemCertificadoLabels.map((_, index) => this.getPredefinedColor(index)),
            label: 'Acessos'
        }],
    };


    private originalData: number[] = [];
    constructor(private userService: UserService) { }

    startDate: string | undefined;
    endDate: string | undefined;

    ngOnInit(): void {
        Chart.register(ChartDataLabels);
        Chart.defaults.set('plugins.datalabels', {
            display: (context: any) => context.dataset.data[context.dataIndex] !== 0,
            color: '#fff',
            anchor: 'end',
            align: 'top',
        });

        this.ajustaData();
        this.loadAlunosMenosEngajados();
        this.loadAlunosMaisEngajados();
        this.loadAlunosSemCertificado();
        this.loadAlunosComMaisAtividades();
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
                const updatedLabels = data.map((item: any) => item[0]);
                const updatedData = data.map((item: any) => item[1]);

                this.chartAlunosMenosEngajadosLabels = [...updatedLabels];
                this.chartAlunosMenosEngajadosData = {
                    ...this.chartAlunosMenosEngajadosData,
                    datasets: [
                        {
                            ...this.chartAlunosMenosEngajadosData.datasets[0],
                            data: [...updatedData],
                            label: 'Acessos',
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
                const updatedLabels = data.map((item: any) => item[0]);
                const updatedData = data.map((item: any) => item[1]);

                this.chartAlunosMaisEngajadosLabels = [...updatedLabels];
                this.chartAlunosMaisEngajadosData = {
                    ...this.chartAlunosMaisEngajadosData,
                    datasets: [
                        {
                            ...this.chartAlunosMaisEngajadosData.datasets[0],
                            data: [...updatedData],
                            label: 'Acessos',
                        },
                    ],
                };
            },
            (error) => {
                console.error('Erro ao carregar os dados dos cursos mais acessados',error);
            }
        );
    }

    loadAlunosSemCertificado(): void {
        this.userService.getAlunosSemCertificado().subscribe(
            (data: any) => {
                const updatedLabels = data.map((item: any) => item[1]);
                const updatedData = data.map((item: any) => item[0]);

                const canvas = <HTMLCanvasElement>document.getElementById('chartAlunosSemCertificadoCanvas');
                const ctx = canvas.getContext('2d');

                this.chartAlunosSemCertificado = new Chart(ctx!, {
                    type: 'bar',
                    data: {
                        labels: [...updatedLabels],
                        datasets: [
                            {
                                label: 'Total de Atividades sem Certificado',
                                data: [...updatedData],
                                backgroundColor: updatedLabels.map((_: any, index: number) => this.getPredefinedColor(index)),
                                borderColor: updatedLabels.map((_: any, index: number) => this.getPredefinedColor(index)),
                                borderWidth: 1
                            },
                        ],
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: {
                                ticks: {
                                    font: {
                                        size: 11,
                                    },
                                    autoSkip: false,
                                    maxRotation: 45,
                                    minRotation: 15,
                                },
                            },
                            y: {
                                ticks: {
                                    font: {
                                        size: 11,
                                    },
                                    stepSize: 3,
                                },
                            },
                        },
                        plugins: {
                            datalabels: {
                                display: true,
                                align: 'end',
                                color: '#000',
                            },
                            tooltip: {
                                callbacks: {
                                    label: function (tooltipItem) {
                                        return `Atividades sem Certificado: ${tooltipItem.raw}`;
                                    },
                                },
                            },
                        },
                    },
                });
            },
            (error) => {
                console.error('Erro ao carregar os alunos sem certificado:', error);
            }
        );
    }


    loadAlunosComMaisAtividades(): void {
        this.userService.getAlunosComMaisAtividades().subscribe((data) => {

            const chartData = data.map((item: any) => ({
                video_title: item[2],
                completion_rate: parseFloat(parseFloat(item[3]).toFixed(2))
            }));

            const canvas = <HTMLCanvasElement>document.getElementById('barChartCanvas');
            const ctx = canvas.getContext('2d');

            this.barChart = new Chart(ctx!, {
                type: 'bar',
                data: {
                    labels: chartData.map((item: any) => item.video_title),
                    datasets: [{
                        label: 'Número de Atividades',
                        data: chartData.map((item: any) => item.completion_rate),
                        backgroundColor: chartData.map((_: any, index: number) => this.getPredefinedColor(index)),
                        borderColor: chartData.map((_: any, index: number) => this.getPredefinedColor(index)),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    indexAxis: 'y',
                    scales: {
                        x: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Número de Atividades',
                            }
                        }
                    },
                    plugins: {
                        datalabels: {
                            display: true,
                            align: 'end',
                            color: '#000'
                        },
                        tooltip: {
                            callbacks: {
                                label: function (tooltipItem) {
                                    return `Número de Atividades: ${tooltipItem.raw}`;
                                }
                            }
                        }
                    }
                }
            });

        });
    }

    getPredefinedColor(index: number): string {
        const predefinedColors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'];
        return predefinedColors[index % predefinedColors.length];
    }

    onChangeDate() {
        this.loadAlunosMenosEngajados();
        this.loadAlunosMaisEngajados();
    }
}
