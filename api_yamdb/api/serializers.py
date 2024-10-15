from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from titles.models import Comment, Review


class ReviewSerializer(serializers.ModelSerializer):
    # author = serializers.SlugRelatedField(
    #     slug_field='username',
    #     read_only=True
    # )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('title_id',)


class CommentSerializer(serializers.ModelSerializer):
    # author = serializers.SlugRelatedField(
    #     slug_field='username',
    #     read_only=True
    # )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('title_id', 'review')
