import { Component, signal } from '@angular/core';
import { NotificationService } from '../services/notification-service';
import { NotificationData } from '../models/notification-data';
import { NewsCard } from '../news-card/news-card';

@Component({
  imports: [NewsCard],
  selector: 'app-archive-page',
  styleUrl: './archive-page.css',
  templateUrl: './archive-page.html',
})
export class ArchivePage {

  userId: number = -1
  notificationsData = signal<NotificationData[]>([]);

  constructor(private notificationService: NotificationService) {}

  ngOnInit(): void {
    this.userId = Number(sessionStorage.getItem("user"))
    this.getUserNotifications();
  }

  getUserNotifications() {
    this.notificationService.getUserNotifications(this.userId).subscribe((notifications) => {
      if (notifications) {
        console.log(notifications);
        this.notificationsData.set(notifications);
      }
    });
  }



}
