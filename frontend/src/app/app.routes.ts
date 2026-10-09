import { Routes } from '@angular/router';
import { LoginPage } from './login-page/login-page';
import { HomePage } from './home-page/home-page';

export const routes: Routes = [
    {
        path: '',
        component: LoginPage
    },
    {
        path: 'home',
        component: HomePage
    }
];
