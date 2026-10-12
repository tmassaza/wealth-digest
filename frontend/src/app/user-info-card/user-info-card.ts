import { Component, Input, Output, EventEmitter} from '@angular/core';
import { User } from '../models/user';
import { Router } from '@angular/router';

@Component({
  imports: [],
  selector: 'app-user-info-card',
  styleUrl: './user-info-card.css',
  templateUrl: './user-info-card.html',
})
export class UserInfoCard {

  @Input() user: User|null = null;
  @Input() notificationsCount: number = 0;
  @Input() isLoading = false;

  @Output() generateNewNotificationEvent = new EventEmitter<void>();

  constructor(private router:Router) {}

  generateNewNotification() {
    this.generateNewNotificationEvent.emit();
  }

  seeArchive() {
    this.router.navigate(['archive']);
  }

}
