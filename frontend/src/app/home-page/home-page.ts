import { Component, signal } from '@angular/core';
import { NewsCard } from '../news-card/news-card';
import { UserInfoCard } from '../user-info-card/user-info-card';
import { UserService } from '../services/user-service';
import { NotificationService } from '../services/notification-service';
import { NotificationNews } from '../models/notification-news';
import { User } from '../models/user';

@Component({
  imports: [NewsCard, UserInfoCard],
  selector: 'app-home-page',
  styleUrl: './home-page.css',
  templateUrl: './home-page.html',
})
export class HomePage {

  lastNotificationDate = signal('');
  lastNotificationNews = signal<NotificationNews[]>([]);
  numberNotificationNews = signal(0);
  notificationsCount = signal(0);

  generateNewNotificationError = signal('');

  user = signal<User|null>(null);

  userId: number = -1;

  isLoading = signal(false);
  
  constructor(private userService: UserService, private notificationService: NotificationService) { }

  ngOnInit(): void {
    this.userId = Number(sessionStorage.getItem("user"))
    this.getUserProfile();
    this.getUserNotificationsCount();
  }

  getUserProfile() {
    this.userService.getUser(this.userId).subscribe((user) => {
      if (user) {
        this.user.set(user);
      }
    })
  }

  getUserNotificationsCount() {
    this.notificationService.getUserNotificationsCount(this.userId).subscribe((count) => {
      this.notificationsCount.set(count);
      if (count > 0) {
        this.getLastNotification();
      }
    });
  }

  getLastNotification() {
    this.notificationService.getUserLastNotification(this.userId).subscribe((notification) => {
      if (notification) {
        this.lastNotificationDate.set(notification.date);
        this.lastNotificationNews.set(notification.notification_news);
        this.numberNotificationNews.set(notification.notification_news.length);
      }
    });
  }

  generateNewNotification() {
    this.isLoading.set(true);
    this.notificationService.getUserNotification(this.userId).subscribe({
      next: (notification) => {
        this.isLoading.set(false);
        console.log(notification);
        if (notification) {
          this.lastNotificationDate.set(notification.date);
          this.lastNotificationNews.set(notification.notification_news);
          this.numberNotificationNews.set(notification.notification_news.length);
        }
      },
      error: (error) => {
        this.generateNewNotificationError.set(error.error.detail)
        this.isLoading.set(false);
      }
    }
    )
  }

  closeErrorBanner() {
    this.generateNewNotificationError.set('');
  }

}
