# PJT10 - Django Pair Programming

> ## 목표
>
> GitHub 협업을 통한 영화 정보 사이트 개발

## APP - Accounts

### 모델링

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



### 회원가입 / 로그인 / 로그아웃

#### 회원가입

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

#### 로그인

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

#### 로그아웃

- Django 내장 함수를 사용하여 로그아웃 코드를 작성한다.

```python
def logout(request):
    auth_logout(request)
    return redirect('movies:index')
```

#### 조건 처리

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

### 유저목록

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

### 유저 상세보기

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



## 느낀점

- 3명이 GitHub을 활용하여 협업프로젝트를 진행하면서 2명에서 진행할 때보다 업무가 명확하게 분리되지 않아 코드가 겹치거나 하는 경우가 많았다. 사전에 충분한 토의가 진행되지 않았던 점이 문제가 되었고, 다음 프로젝트부터는 명확한 기능 분담의 필요성을 느꼈다. 또한 처음에는 복잡하던 fork와 branch 기능이 협업을 진행하면서 그 무엇보다 편리한 기능임을 느꼈다.