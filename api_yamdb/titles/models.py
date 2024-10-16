from django.db import models


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
