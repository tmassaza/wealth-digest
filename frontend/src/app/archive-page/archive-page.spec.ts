import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ArchivePage } from './archive-page';

describe('ArchivePage', () => {
  let component: ArchivePage;
  let fixture: ComponentFixture<ArchivePage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ArchivePage],
    }).compileComponents();

    fixture = TestBed.createComponent(ArchivePage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
