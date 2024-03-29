# :notebook_with_decorative_cover: PJT10 - Django Pair Programming

> ## 목표
>
> GitHub 협업을 통한 영화 정보 사이트 개발

<br>

---

:heavy_check_mark: 데이터베이스 ERD

![1321322](https://user-images.githubusercontent.com/52685250/69314534-bf661000-0c77-11ea-945e-c7042576fa24.JPG)

---

<br>

## :one: APP - Accounts

### (1)모델링

- 기존 Django에서 제공하는 AbstractUser 모델을 상속받아 User 모델을 재설계한다.

```python
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="followings")
```

- Django에서 기본적으로 설정되어 있는 User 모델을 accounts 앱에서 재설계 하였으므로, `settings.py`에서 이를 명시해줄 필요가 있다.

```python
# settings.py
...
AUTH_USER_MODEL = 'accounts.User' # 기본 User모델 재선언
```

<br>

### (2)회원가입 / 로그인 / 로그아웃

#### ①회원가입

- 회원가입 양식을 보여줄 form을 생성한다
- 기본 `UserCreationForm`에 `email` field를 추가해준다.

```python
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('email',)
```

- `GET` 과 `POST` 방식을 구분하여 처리할 동작을 코딩한다.

```python
def signup(request):
    if request.user.is_authenticated: # 로그인이 되어 있는 경우
        return redirect('accounts:index')
    if request.method == 'POST': # POST 요청
        form = CustomUserCreationForm(request.POST)
        if form.is_valid(): # 유효성 검사
            user = form.save() # user 정보 저장
            auth_login(request, user) # 로그인
            return redirect('accounts:index')
    else: # GET 요청
        form = CustomUserCreationForm()
    context = {'form': form,}
    return render(request, 'accounts/authform.html', context)
```

- GET 방식으로 요청을 받을 경우 회원가입 form을 보여주고, POST 방식으로 받을 경우 입력된 정보를 DB에 저장하는 동시에 로그인한다.

```html
{% if request.resolver_match.url_name == 'signup' %}
  <h1>SIGNUP</h1>  
{% else %}
  <h1>LOGIN</h1>
{% endif %}
  <form action="" method="POST">
    {% csrf_token %}
    {% bootstrap_form form %}
    <input type="submit" value="제출">
  </form>
```



![image](https://user-images.githubusercontent.com/52814897/69311506-d0ab1e80-0c6f-11ea-8088-14d13a75b28f.png)

#### ②로그인

- 유저의 login 여부를 확인하여 로그인 되어 있을 겨우 index 페이지로 보낸다.

```python
if request.user.is_authenticated:
        return redirect('movies:index')
```

- `GET`방식과 `POST`방식으로 요청을 받을 수 있으며, GET 방식에서는 로그인 폼을 보여주고, POST 방식으로 요청을 받을 경우 로그인을 실행한다.

```python
if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid(): # 유효성 검사
            auth_login(request, form.get_user()) # 로그인
            return redirect(request.GET.get('next') or 'movies:index')
    else:
        form = AuthenticationForm()
    context = {'form': form,}
    return render(request, 'accounts/authform.html', context)
```

![image](https://user-images.githubusercontent.com/52814897/69312048-3ba92500-0c71-11ea-8dd5-fb7c8e4b4a43.png)

#### ③로그아웃

- Django 내장 함수를 사용하여 로그아웃 코드를 작성한다.

```python
def logout(request):
    auth_logout(request)
    return redirect('movies:index')
```

#### ④조건 처리

- 각각의 로그인/비로그인 상태에서 보여질 nav bar를 조건에따라 처리한다.

```html
{% if request.user.is_authenticated %}
<li class="nav-item">
	<a class="nav-link" href="{% url 'accounts:index' %}">유저정보</a>
</li>
<li class="nav-item">
	<a class="nav-link" href="{% url 'accounts:logout' %}">로그아웃</a>
</li>
{% else %}
<li class="nav-item">
	<a class="nav-link" href="{% url 'accounts:signup' %}">회원가입</a>
</li>
<li class="nav-item">
	<a class="nav-link" href="{% url 'accounts:login' %}">로그인</a>
</li>
{% endif %}
```

![image](https://user-images.githubusercontent.com/52814897/69312330-f9341800-0c71-11ea-9d08-fe613d696ef7.png)
![image](https://user-images.githubusercontent.com/52814897/69312342-005b2600-0c72-11ea-8d8c-4c2c3887514d.png)

<br>

### (3)유저목록

- `get_user_model().objects.all()`: DB에 저장되어있는 모든 유저 객체를 불러온다.

```python
def index(request):
    users = get_user_model().objects.all() 
    context = {'users': users,}
    return render(request, 'accounts/index.html', context)
```

- context로 받은 users의 모든 객체를 출력한다.
- 각 유저의 username을 클릭하면 user의 상세 페이지로 이동한다.

```html
{% for user in users %}
<a href="{% url 'accounts:detail' user.pk %}" class="btn btn-success">
  {{ user.username }}
</a>
```

![image](https://user-images.githubusercontent.com/52814897/69313356-ac057580-0c74-11ea-9a5c-9d1f37714d9d.png)

<br>

### (4)유저 상세보기

- 유저의 정보만 context에 담아 templates으로 보내준다

```python
def detail(request, user_pk):
    auth_user = get_object_or_404(get_user_model(), pk=user_pk)
    context = {'auth_user': auth_user,}
    return render(request, 'accounts/detail.html', context)
```

- 유저가 작성한 댓글과 평점을 불러오기 위해 templates에서 `Review Model`을 역참조한다.

```html
<h3>내가 작성한 댓글과 평점</h3>
{% for review in auth_user.review_set.all %}
	<p>{{ review.content }} || {{ review.score }}점 </p>
{% endfor %}
```

![image](https://user-images.githubusercontent.com/52814897/69313426-d3f4d900-0c74-11ea-8fd0-cebabd3ae13b.png)

- 유저가 좋아요한 영화 목록과 팔로워 정보도 각각 `ManyToMany`필드에서 설정한 `related_name`을 불러와 보여준다.

```html
<h3>내가 좋아요한 영화 정보</h3>
{% for movie in auth_user.like_movies.all %}
  <a href="{% url 'movies:detail' movie.pk %}"><p>{{ movie.title }}</p></a>
{% endfor %}

<!-- #### -->

<h3>팔로워 정보</h3>
{% with followings=auth_user.followings.all followers=auth_user.followers.all %}
<p>팔로잉 : {{ followings|length }} / 팔로워 : {{ followers|length }} </p>
{% endwith %}
```

![image](https://user-images.githubusercontent.com/52814897/69313446-e2db8b80-0c74-11ea-9f13-616b109bc31e.png)

<br>

## :two: APP - Movies

### (1)모델링

```python
# movies app의 models.py

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
    # 장르 정보는 Genre model과 M:N 관계로 이루어져 있다.(한 영화당 장르가 여러 개일 수 있고 장르당 영화가 여러개 일 수 있기 때문)
    genre = models.ManyToManyField(Genre, related_name='genre_movies', blank=True)
    # like_users(좋아요를 누른 유저 정보) => M:N 관계로 이루어져 있다.
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_movies', blank=True)

    class Meta:
        ordering = ('-pk',)


class Review(models.Model):
    content = models.CharField(max_length=140)
    score = models.IntegerField()
    # movie : review = 1 : N 관계이므로 ForeignKey를 이용해 모델링했다.
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    # review : user = 1 : N 관계이므로 ForeignKey를 이용해 모델링했다.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-pk',)
```

<br>

### (2)영화 목록

- 영화의 이미지를 클릭하면 `영화 상세보기` 페이지로 이동

```python
#movies app 의 view.py

def index(request):
    movies = Movie.objects.all()
    context = {'movies': movies,}
    return render(request, 'movies/index.html', context)
```

```html
<!-- movies app의 index.html -->

<h1 class="text-center" style="font-family: 'Do Hyeon';">영화 목록</h1>
<hr>
<div class="row">
  {% for movie in movies %} <!-- movies에 있는 movie를 출력 -->
  <div class="col-sm-6 col-md-4 mb-5">
    <div class="card">
      <a href="{% url 'movies:detail' movie.pk %}"><img src="{{movie.poster_url}}" class="card-img-top"
          alt="{{movie.title}}"></a> <!-- movie detail 페이지로 이동 -->
      <div class="card-body">
        <h5 class="card-title">{{movie.title}}</h5>
        <hr>
        <b>{{ movie.like_users.all|length }}</b>명의 좋아요!
      </div>
    </div>
  </div>
  {% endfor %}
```

![image](https://user-images.githubusercontent.com/52685242/69311691-49aa7600-0c70-11ea-80df-6fe24f37a20e.png)

<br>

### (3)영화 상세보기

- 영화 관련 정보가 모두 나열

```python
# movies app의 detail.py

def detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    reviews = movie.review_set.all() # reviews 를 출력
    review_form = ReviewForm()
    context = {'movie': movie, 'review_form': review_form, 'reviews': reviews,}
    return render(request, 'movies/detail.html', context)
```

```html
<!-- movies app의 detail.html -->

<font color="#3E64E2"><h1 class="text-center" style="font-family: 'Do Hyeon';">영화 정보 조회</h1></font>
  <br>
  <table border="2px solid black"> <!-- 영화에 대한 정보를 테이블로 표현 -->
    <thead>
      <tr height="30px">
        <th class="text-center" width="100px">분류</th>
        <th class="text-center">내용</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="text-align: center;">title</td>
        <td>{{ movie.title }}</td>
      </tr>
      <tr>
        <td style="text-align: center;">audience</td>
        <td>{{ movie.audience }}</td>
      </tr>
      <tr>
        <td style="text-align: center;">genre</td>
        <td>{% for genre in movie.genre.all %} <!-- 한 영화에 대한 중복으로 설정된 장르들을 출력 -->
            {{ genre.name }}
            {% endfor %}
        </td>
      </tr>
      <tr>
        <td style="text-align: center;">poster_url</td>
        <td><a href="{{ movie.poster_url }}" target="_blank">{{ movie.poster_url }}</a></td> <!-- a태그로 웹 페이지로 연결 -->
      </tr>
      <tr>
        <td style="text-align: center;">description</td>
        <td>{{ movie.description }}</td>
      </tr>
    </tbody>
  </table>
```

![image](https://user-images.githubusercontent.com/52685242/69307504-2979b780-0c6e-11ea-97ce-04378d583b04.png)

<br>

### (4)평점 생성

- 영화 평점은 로그인 한 사람만 이용 가능

```python
# movies app의 views.py

@require_POST
def reviews_create(request, movie_pk):
    if request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False) # commit=False로 객체는 만들지만 잠시 DB에는 저장하지 않고
            review.movie_id = movie_pk # 작성 리뷰의 영화 id 값과 movie_pk를 일치하고,
            review.user = request.user # 리뷰를 작성한 유저와 요청한 유저를 일치 시킨후
            review.save() # 그 다음에 review 객체를 저장한다.
            return redirect('movies:detail', movie_pk) # 영화 정보 생성시 유효성 검증까지 올바르게 완료되면 각 영화의 상세보기 페이지로 redirect
        else:
            return redirect('movies:index')
    return HttpResponse('No movie information', status=404)
```

```django
<!-- movies app의 detail template 일부(댓글 작성 부분) -->

<p><b>{{ reviews|length }}개의 댓글</b></p>
{% for review in reviews %}
  <div>
    댓글 : {{ review.content }} - {{ review.score }}점
    {% if request.user == review.user %}
      <form action="{% url  'movies:reviews_delete' movie.pk review.pk %}" method="POST" style="display: inline;">
        {% csrf_token %}
        <input type="submit" value="DELETE">
      </form>
    {% endif %}
  </div>
{% empty %}
  <p><b>댓글이 없어요...</b></p>
{% endfor %}
<hr>
{% if user.is_authenticated %} <!-- is_authenticated를 통해 로그인 한 유저만 댓글 작성 form이 나오도록 작성했다. -->
  <form action="{% url 'movies:reviews_create' movie.pk %}" method="POST">
    {% csrf_token %}
    {{ review_form }}
    <input type="submit" value="submit">
  </form>
{% else %} <!-- 로그인이 안 된 상태에서는 로그인 페이지로 이동할 수 있도록 설계 -->
  <a href="{% url 'accounts:login' %}">[댓글을 작성하려면 로그인하세요]</a>
{% endif %}
```

![image](https://user-images.githubusercontent.com/52685242/69307560-56c66580-0c6e-11ea-9805-02cf02ca9620.png)

<br>

### (5)평점 삭제

- 영화 평점 삭제는 본인만 가능
- 데이터베이스에서 삭제되면, 해당하는 영화의 `영화 상세보기` 페이지로 Redirect 합니다.

```python
# movie app의 views.py

@require_POST
def reviews_delete(request, movie_pk, review_pk):
    if request.user.is_authenticated: # 로그인을 한 상태이고
        review = get_object_or_404(Review, pk=review_pk)
        if request.user == review.user: # 작성한 리뷰의 유저와 요청한 유저와 일치할 때만
            review.delete() # 리뷰 삭제 가능
        return redirect ('movies:detail', movie_pk)
    return HttpResponse('No movie information', status=404)
```

```html
<!-- movie app의 detail template의 댓글 삭제 부분 -->

{% for review in reviews %}
  <div>
    댓글 : {{ review.content }} - {{ review.score }}점
    {% if request.user == review.user %} <!-- 요청한 유저와 작성한 리뷰의 유저와 일치하는 경우에만 DELETE 버튼이 보여진다. -->
      <form action="{% url  'movies:reviews_delete' movie.pk review.pk %}" method="POST" style="display: inline;">
        {% csrf_token %}
        <input type="submit" value="DELETE">
      </form>
    {% endif %}
  </div>
{% empty %}
  <p><b>댓글이 없어요...</b></p>
{% endfor %}
```

![image](https://user-images.githubusercontent.com/52685242/69307657-a0af4b80-0c6e-11ea-80b9-da360d8eccce.png)

<br>

### (6)영화 좋아요 기능 구현

- 좋아하는 영화를 담아 놓을 수 있도록 구현
- 로그인 한 유저만 해당 기능을 사용 가능

```python
# movie app의 views.py

@login_required
def like(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if movie.like_users.filter(pk=request.user.pk).exists(): # 각 영화의 좋아요를 누른 사람들의 정보들 중 요청한 유저 정보가 있는 경우
        movie.like_users.remove(request.user) # like_users에서 요청한 유저를 삭제한다.
    else: # 아닌 경우
        movie.like_users.add(request.user) # like_users에서 요청한 유저를 추가한다.
    return redirect('movies:detail', movie_pk)
```

```html
<!-- movie app의 detail template의 좋아요 기능 부분 -->

<a href="{% url 'movies:like' movie.pk %}">
  {% if user in movie.like_users.all %} <!-- 요청한 유저가 각 영화의 좋아요를 누른 유저들의 정보에 포함되어 있는 경우 -->
    <button class="btn btn-warning">좋아요 취소...</button> <!-- 좋아요 취소 버튼이 보이게 한다. -->
  {% else %} <!-- 아닌 경우 -->
    <button class="btn btn-danger">좋아요!</button> <!-- 좋아요로 보이게 한다. -->
  {% endif %}
</a>
```

![image](https://user-images.githubusercontent.com/52685242/69311744-71014300-0c70-11ea-8881-a037942351fc.png)

<br>

## :three: 느낀점

:heavy_check_mark: <b>김기은</b>

-  3명이 GitHub을 활용하여 협업프로젝트를 진행하면서 2명에서 진행할 때보다 업무가 명확하게 분리되지 않아 코드가 겹치거나 하는 경우가 많았다. 사전에 충분한 토의가 진행되지 않았던 점이 문제가 되었고, 다음 프로젝트부터는 명확한 기능 분담의 필요성을 느꼈다. 또한 처음에는 복잡하던 fork와 branch 기능이 협업을 진행하면서 그 무엇보다 편리한 기능임을 느꼈다. 

<br>

:heavy_check_mark: <b>심규현</b>

- 다른 조와 달리 3명이서 Pair Programming 프로젝트를 수행했다. 역할을 더 상세하게 분담했기 때문에 프로젝트를 만드는데 수월했으나 github의 fork로 협업을 수행하면서 git branch가 꼬이거나 작성했던 코드가 사라지는 등 어려움이 있었다.
- 하지만 이번 프로젝트를 통해 앞으로 진행할 Final Project에서 github 협업으로 프로젝트를 만들어야 하는데 이번 프로젝트에서 여러 시행착오를 겪으면서 github branch와 fork의 개념을 확실하게 익힐 수 있었고 또한 오랜만에 django 프로젝트를 했는데 django CRUD의 큰 흐름을 다시 한 번 복습할 수 있었다.

<br>

:heavy_check_mark: <b>이가경</b>

-  github의 협업이 익숙치 않아 코딩도 전에 발생하는 문제가 많았다. 하지만 익숙해진다면 정말 좋은 협업툴이 될것이라고 생각한다. 또한, 협업에 대해서 생각보다 업무분담 혹은 작업속도 측면에서 차이가 심했다. 특히 내 자신의 Django 실력부족은 꼭 극복해야 할 문제점이라 느꼈다. 이번 프로젝트를 통해 어떻게서든 Django 실력을 향상시켜 팀원에 민폐 안끼치고 성공적으로 프로젝트 마무리 할 수 있도록 노력하겠다. 