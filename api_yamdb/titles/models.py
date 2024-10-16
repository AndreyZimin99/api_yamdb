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
    description = models.TextField('Описание')
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
