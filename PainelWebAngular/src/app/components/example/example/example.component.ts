import { ExampleData } from './../../../models/example-data.model';
import { ApiService } from './../../../api.service';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-example',
  templateUrl: './example.component.html',
  styleUrls: ['./example.component.scss']
})
export class ExampleComponent implements OnInit {

  data: ExampleData[] | undefined;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.apiService.get<ExampleData[]>('example-endpoint').subscribe(
      (response) => {
        this.data = response;
        console.log(this.data);
      },
      (error) => {
        console.error('Erro ao buscar dados:', error);
      }
    );
  }
}
