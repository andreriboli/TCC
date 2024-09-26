import { HomeComponent } from './components/components/home/home.component';
import { ConsultaComponent } from './components/components/consulta/consulta.component';
import { GraficosComponent } from './components/components/graficos/graficos.component';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MenuComponent } from './components/components/menu/menu.component';

const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },  // Redireciona para Home por padrão
  { path: 'home', component: HomeComponent },  // Rota para a Home
  { path: 'consulta', component: ConsultaComponent },  // Rota para a página de Consultas
  { path: 'graficos', component: GraficosComponent },  // Rota para a página de Gráficos
  { path: 'menu', component: MenuComponent },  // Rota para o Menu
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
