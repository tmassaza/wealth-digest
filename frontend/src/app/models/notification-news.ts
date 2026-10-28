import { NotificationProduct } from './notification-product';

export interface NotificationNews {
    title: string,
    date: string,
    summary: string,
    relevance: string,
    source: string,
    link: string,
    products: NotificationProduct[]
}
