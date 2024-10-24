import { Component, OnInit, ViewChild } from '@angular/core';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartOptions, Chart, ChartDataset } from 'chart.js';
import DataLabelsPlugin from 'chartjs-plugin-datalabels';
import { UserService } from '../../services/user.service';
import { CategoryService } from '../../services/category.service';
import { VimeoService } from '../../services/vimeo.service';

@Component({
    selector: 'app-home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss'],
})
export class HomeComponent implements OnInit {

    @ViewChild(BaseChartDirective) chart: BaseChartDirective | undefined;
    @ViewChild(BaseChartDirective, { static: false }) scatterChartCanvas: BaseChartDirective | undefined;
    @ViewChild('chartCurso', { static: false }) chartCurso: BaseChartDirective | undefined;


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
                    return context.dataset.data[context.dataIndex] !== 0;
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
        datasets: [{
            data: [], label: 'Usuários Logados', backgroundColor: [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'
            ],
        }],
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
                    label: function (context) {
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

    public scatterChartOptions: ChartOptions = {
        responsive: true,
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Views',
                },
            },
            y: {
                title: {
                    display: true,
                    text: 'Unique Viewers Percentage',
                },
                ticks: {
                    callback: (value) => value + '%'
                }
            }
        },
        plugins: {
            datalabels: {
                display: false
            },
            tooltip: {
                callbacks: {
                    label: function (tooltipItem) {
                        const raw = tooltipItem.raw as { x: number, y: number };
                        return `Views: ${raw.x}, Unique Viewer %: ${raw.y}`;
                    }
                }
            }
        }
    };


    public scatterChartData: ChartDataset<'scatter', { x: number, y: number }[]>[] = [
        {
            label: 'Engagement',
            data: [],
            backgroundColor: 'rgba(75,192,192,1)',
            borderColor: 'rgba(75,192,192,1)',
            pointHoverBackgroundColor: 'rgba(75,192,192,1)',
            pointHoverBorderColor: 'rgba(220,220,220,1)',
            showLine: false
        }
    ];

    scatterChart: Chart | undefined;
    startDate: string;
    endDate: string;
    barChart:  Chart | undefined;

    constructor(
        private userService: UserService,
        private categoryService: CategoryService,
        private vimeoService: VimeoService
    ) {
        Chart.register(DataLabelsPlugin);

        Chart.defaults.set('plugins.datalabels', {
            display: (context: any) => context.dataset.data[context.dataIndex] !== 0,
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
        this.loadVideosComMelhorConclusao();
        this.loadVideosMaisEngajados();
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
        this.userService.getUltimosUsuariosLogados(this.startDate, this.endDate).subscribe(
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

            this.chartCursosByCategoriaLabels = data.map((item: any) => item[1]);
            this.chartCursosByCategoriaData.datasets[0].data = data.map((item: any) => item[2]);

            if (this.scatterChartCanvas) {
                this.scatterChartCanvas.update();
            }
        }, error => {
            console.error('Erro ao carregar os dados de categorias:', error);
        });
    }


    loadVideosMaisEngajados(): void {
        setTimeout(() => {
            this.vimeoService.getVideosMaisEngajados().subscribe((data: any) => {
                const chartData = data.map((item: any) => ({
                    x: item[1],
                    y: parseFloat(parseFloat(item[3]).toFixed(2))
                }));

                this.createScatterChart(chartData);

            }, error => {
                console.error('Erro ao carregar os vídeos mais engajados', error);
            });
        }, 1000);
    }

    createScatterChart(chartData: any): void {
        const canvas = <HTMLCanvasElement>document.getElementById('scatterChartCanvas');
        const ctx = canvas.getContext('2d');

        this.scatterChart = new Chart(ctx!, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Engajamento',
                    data: chartData,
                    backgroundColor: 'rgba(121, 178, 233, 1)',
                    borderColor: 'rgba(121, 178, 233, 1)',
                    pointHoverBackgroundColor: 'rgba(121, 178, 233, 1)',
                    pointHoverBorderColor: 'rgba(220, 220, 220, 1)',
                    showLine: false
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Views'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Percentual de Visualizador Único'
                        },
                        ticks: {
                            callback: (value) => value + '%'
                        }
                    }
                },
                plugins: {
                    datalabels: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function (tooltipItem) {
                                const raw = tooltipItem.raw as { x: number, y: number };
                                return `Views: ${raw.x}, Visualizador Único %: ${raw.y}`;
                            }
                        }
                    }
                }
            }
        });
    }

    loadVideosComMelhorConclusao(): void {
        this.vimeoService.getVideosComMelhorConclusao().subscribe((data: any) => {
            const chartData = data.map((item: any) => ({
                video_title: item[0],
                completion_rate: parseFloat(parseFloat(item[3]).toFixed(2))
            }));

            this.createBarChart(chartData);
        });
    }

    createBarChart(chartData: any): void {
        const canvas = <HTMLCanvasElement>document.getElementById('barChartCanvas');
        const ctx = canvas.getContext('2d');

        this.barChart = new Chart(ctx!, {
            type: 'bar',
            data: {
                labels: chartData.map((item: any) => item.video_title),
                datasets: [{
                    label: 'Taxa de Conclusão (%)',
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
                            text: 'Taxa de Conclusão (%)'
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
                                return `Taxa de Conclusão: ${tooltipItem.raw}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    getPredefinedColor(index: number): string {
        const predefinedColors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'];
        return predefinedColors[index % predefinedColors.length];
    }

    onChangeDate() {
        this.loadUltimosUsuariosLogados();
        this.loadCategoriaUsuariosData();
    }
}
