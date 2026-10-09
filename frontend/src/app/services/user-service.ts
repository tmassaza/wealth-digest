import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Service, inject } from '@angular/core';
import {environment} from '../../environments/environment';

import { User } from '../models/user';

@Service()
export class UserService {

    private http = inject(HttpClient);
    private userApiUrl = 'http://localhost:8000' + '/users/';

    getUsers(): Observable<User[]> {
        return this.http.get<User[]>(this.userApiUrl);
    }

    getUser(userId: number): Observable<User> {
        return this.http.get<User>(this.userApiUrl + userId);
    }

}
