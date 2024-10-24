from django.contrib import admin

from .models import Comment, Review


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'score', 'pub_date')
    list_filter = ('score', 'pub_date', 'author')
    search_fields = ('text', 'author__username', 'title__name')
    ordering = ('-pub_date',)
    raw_id_fields = ('title', 'author')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'author', 'pub_date')
    list_filter = ('pub_date', 'author')
    search_fields = ('text', 'author__username', 'review__text')
    ordering = ('-pub_date',)
    raw_id_fields = ('review', 'author')


admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
