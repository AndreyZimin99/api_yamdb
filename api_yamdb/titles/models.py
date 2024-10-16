from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Title(models.Model):
    name = models.TextField('Текст публикации')
    year = models.IntegerField(
        'Год выпуска',
    )
    description = models.TextField(
        'Описание книги',
        null=True,
        blank=True
    )

    class Meta:
        default_related_name = 'Titles'

    def __str__(self):
        return self.name[:30]


class Review(models.Model):
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
