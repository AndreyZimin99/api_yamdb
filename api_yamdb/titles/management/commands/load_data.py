import csv
from django.core.management.base import BaseCommand
from users.models import User
from titles.models import Category, Genre, Title, GenreTitle
from reviews.models import Review, Comment


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.load_users()
        self.load_categories()
        self.load_genres()
        self.load_titles()
        self.load_genre_titles()
        self.load_reviews()
        self.load_comments()

    def load_users(self):
        with open('static/data/users.csv', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            n = 0
            for row in reader:
                User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    role=row[3],
                    bio=row[4],
                    first_name=row[5],
                    last_name=row[6],
                ).save()
                n += 1
                print(f'done {n}')

    def load_categories(self):
        with open('static/data/category.csv', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            categories = []
            for row in reader:
                categories.append(Category(
                    name=row[1],
                    slug=row[2],
                ))
            Category.objects.bulk_create(categories)
            print(f'done {len(categories)}')

    def load_genres(self):
        with open('static/data/genre.csv', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            genres = []
            for row in reader:
                genres.append(Genre(
                    name=row[1],
                    slug=row[2],
                ))
            Genre.objects.bulk_create(genres)
            print(f'done {len(genres)}')

    def load_titles(self):
        with open('static/data/titles.csv', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            titles = []
            for row in reader:
                category = Category.objects.get(id=row[3])
                titles.append(Title(
                    name=row[1],
                    year=row[2],
                    category=category
                ))
            Title.objects.bulk_create(titles)
            print(f'done {len(titles)}')

    def load_genre_titles(self):
        with open('static/data/genre_title.csv', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            genre_titles = []
            for row in reader:
                title_id = Title.objects.get(id=row[1])
                genre_id = Genre.objects.get(id=row[2])
                genre_titles.append(GenreTitle(
                    title=title_id,
                    genre=genre_id
                ))
            GenreTitle.objects.bulk_create(genre_titles)
            print(f'done {len(genre_titles)}')

    def load_reviews(self):
        with open('static/data/review.csv', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            reviews = []
            for row in reader:
                title = Title.objects.get(id=row[1])
                author = User.objects.get(id=row[3])
                reviews.append(Review(
                    title=title,
                    text=row[2],
                    author=author,
                    score=row[4],
                    pub_date=row[5],
                ))
            Review.objects.bulk_create(reviews)
            print(f'done {len(reviews)}')

    def load_comments(self):
        with open('static/data/comments.csv', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            comments = []
            for row in reader:
                review = Review.objects.get(id=row[1])
                author = User.objects.get(id=row[3])
                comments.append(Comment(
                    review=review,
                    text=row[2],
                    author=author,
                    pub_date=row[4],
                ))
            Comment.objects.bulk_create(comments)
            print(f'done {len(comments)}')
