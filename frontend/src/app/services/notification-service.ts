import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Service, inject } from '@angular/core';
import {environment} from '../../environments/environment';
import { NotificationData } from '../models/notification-data';

@Service()
export class NotificationService {

    private http = inject(HttpClient);
    private notificationApiUrl = 'http://localhost:8000' + '/notifications/users/';

    getUserNotifications(userId: number): Observable<NotificationData[]> {
        return this.http.get<NotificationData[]>(this.notificationApiUrl + userId + '/list');
    }

    getUserNotificationsCount(userId: number): Observable<number> {
        return this.http.get<number>(this.notificationApiUrl + userId + '/list/count');
    }

    getUserLastNotification(userId: number): Observable<NotificationData> {
        return this.http.get<NotificationData>(this.notificationApiUrl + userId + '/last');
    }

    getUserNotification(userId: number): Observable<NotificationData> {
        return this.http.get<NotificationData>(this.notificationApiUrl + userId);
    }

}
