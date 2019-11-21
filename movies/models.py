from django.db import models
from django.conf import settings

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=20)


class Movie(models.Model):
    title = models.CharField(max_length=30)
    audience = models.IntegerField()
    poster_url = models.CharField(max_length=140)
    description = models.TextField()
    genre = models.ManyToManyField(Genre, related_name='genre_movies', blank=True)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_movies', blank=True)

    class Meta:
        ordering = ('-pk',)


class Review(models.Model):
    content = models.CharField(max_length=140)
    score = models.IntegerField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-pk',)