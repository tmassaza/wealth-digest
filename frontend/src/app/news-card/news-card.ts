import { Component, Input, OnInit } from '@angular/core';
import { NotificationNews } from '../models/notification-news';

@Component({
  imports: [],
  selector: 'app-news-card',
  styleUrl: './news-card.css',
  templateUrl: './news-card.html',
})
export class NewsCard {

  @Input() news!: NotificationNews;

  ngOnInit(): void {
  }


}
