from django.db import models

from users.models import User
from titles.models import Title


class Review(models.Model):
    """"Модель отзыва."""
    SCORE_CHOICES = [(i, str(i)) for i in range(1, 11)]
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='reviews'
    )
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор отзыва',
    )
    score = models.IntegerField('Рейтинг', choices=SCORE_CHOICES)
    pub_date = models.DateTimeField(
        'Дата публикации отзыва', auto_now_add=True,
    )

    class Meta:
        default_related_name = 'reviews'
        unique_together = ('title', 'author')
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pub_date']

    def __str__(self):
        return f'{self.text}, {self.title}, {self.author}'


class Comment(models.Model):
    """"Модель комментария к отзыву."""
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
    )
    pub_date = models.DateTimeField(
        'Дата добавления комментария',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']

    def __str__(self):
        return f'{self.text}, {self.review}, {self.author}'
