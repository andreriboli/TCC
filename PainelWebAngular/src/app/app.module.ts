import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HttpClientModule } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HomeComponent } from './components/components/home/home.component';
import { GraficosComponent } from './components/components/graficos/graficos.component';
import { FormsModule } from '@angular/forms';
import { NgChartsModule } from 'ng2-charts';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { AlunosComponent } from './components/components/alunos/alunos.component';
import { ProfessoresComponent } from './components/components/professores/professores.component';
import { CursosComponent } from './components/components/cursos/cursos.component';


@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    GraficosComponent,
    SidebarComponent,
    AlunosComponent,
    ProfessoresComponent,
    CursosComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    BrowserAnimationsModule,
    FormsModule,
    NgChartsModule

  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
