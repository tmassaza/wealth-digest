import { Component, signal } from '@angular/core';
import { UserService } from '../services/user-service';
import { User } from '../models/user';
import { Router } from '@angular/router';

@Component({
  imports: [],
  selector: 'app-login-page',
  styleUrl: './login-page.css',
  templateUrl: './login-page.html',
})
export class LoginPage {

  users = signal<User[]>([]);

  constructor(private userService: UserService, private router: Router) {}

   ngOnInit(): void {
    this.getUsers();
  }

  getUsers() {
    this.userService.getUsers().subscribe((users) => {
      this.users.set(users);
    })
  }

  selectUser(userId: number) {
    sessionStorage.setItem('user', userId.toString())
    this.router.navigate(['home'])
  }

}
