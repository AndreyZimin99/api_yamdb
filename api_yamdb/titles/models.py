from django.db import models
from .validators import valid_date


class Category(models.Model):
    name = models.CharField('Категория', max_length=50)
    slug = models.SlugField('Слаг', unique=True, max_length=256)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=50)
    slug = models.SlugField('Слаг', unique=True, max_length=256)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField('Имя произведения', max_length=256)
    year = models.SmallIntegerField('Год выпуска', validators=[valid_date])
    description = models.CharField('Описание')
    genre = models.ManyToManyField(Genre, related_name='titles',
                                   verbose_name='Жанр')
    category = models.ForeignKey(Category, related_name='titles',
                                 on_delete=models.SET_NULL, null=True,
                                 verbose_name='категория')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']

    def __str__(self):
        return self.name


class Review(models.Model):
    """"Модель отзыва."""
    SCORE_CHOICES = [(i, str(i)) for i in range(1, 11)]
    # title_id = models.ForeignKey(
    #     Title,
    #     on_delete=models.CASCADE,
    #     verbose_name='Id Произведения',
    # )
    title_id = models.IntegerField()
    # author = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     verbose_name='Автор отзыва',
    # )
    author = models.IntegerField('Автор отзыва')
    text = models.TextField('Текст отзыва')
    score = models.IntegerField('Рейтинг', choices=SCORE_CHOICES)
    pub_date = models.DateTimeField(
        'Дата публикации отзыва', auto_now_add=True,
    )

    class Meta:
        default_related_name = 'reviews'

    def __str__(self):
        return f'{self.text}, {self.title_id}, {self.author}'


class Comment(models.Model):
    """"Модель комментария к отзыву."""
    # author = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     verbose_name='Автор публикации',
    # )
    author = models.IntegerField()
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
    )
    text = models.TextField('Текст комментария')
    pub_date = models.DateTimeField(
        'Дата добавления комментария',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        default_related_name = 'comments'

    def __str__(self):
        return f'{self.text}, {self.review}, {self.author}'
