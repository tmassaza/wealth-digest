import { Component, Input, Output, EventEmitter} from '@angular/core';
import { User } from '../models/user';

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
  

  generateNewNotification() {
    this.generateNewNotificationEvent.emit();
  }

}
