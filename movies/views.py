from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_POST
from .models import Genre, Movie, Review
from .forms import ReviewForm

# Create your views here.
def index(request):
    movies = Movie.objects.all()
    context = {'movies': movies,}
    return render(request, 'movies/index.html', context)


def detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    reviews = movie.review_set.all()
    review_form = ReviewForm()
    context = {'movie': movie, 'review_form': review_form, 'reviews': reviews,}
    return render(request, 'movies/detail.html', context)

@require_POST
def reviews_create(request, movie_pk):
    if request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.movie_id = movie_pk
            review.user = request.user
            review.save()
            return redirect('movies:detail', movie_pk)
        else:
            return redirect('movies:index')
    return HttpResponse('No movie information', status=404)


@require_POST
def reviews_delete(request, movie_pk, review_pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        if request.user == review.user:
            review.delete()
        return redirect ('movies:detail', movie_pk)
    return HttpResponse('No movie information', status=404)


@login_required
def like(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if movie.like_users.filter(pk=request.user.pk).exists():
        movie.like_users.remove(request.user)
    else:
        movie.like_users.add(request.user)
    return redirect('movies:detail', movie_pk)