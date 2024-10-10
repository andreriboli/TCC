import { HomeComponent } from './components/components/home/home.component';
import { ConsultaComponent } from './components/components/consulta/consulta.component';
import { GraficosComponent } from './components/components/graficos/graficos.component';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MenuComponent } from './components/components/menu/menu.component';
import { CursosComponent } from './components/components/cursos/cursos.component';
import { AlunosComponent } from './components/components/alunos/alunos.component';
import { ProfessoresComponent } from './components/components/professores/professores.component';

const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent },
  { path: 'cursos', component: CursosComponent },
  { path: 'alunos', component: AlunosComponent },
  { path: 'professores', component: ProfessoresComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
