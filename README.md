# 10 - Django (Pair Programming)

## 1. 목표

- 협업을 통한 데이터베이스 모델링 및 기능 구현
- 데이터베이스 설계

![1574314691132](C:\Users\student\AppData\Roaming\Typora\typora-user-images\1574314691132.png)

## 2. 구현 내용

### `movies` App

1. ##### 영화 목록

   - 영화의 이미지를 클릭하면 `영화 상세보기` 페이지로 이동

   ![image](https://user-images.githubusercontent.com/52685242/69311691-49aa7600-0c70-11ea-80df-6fe24f37a20e.png)

2. ##### 영화 상세보기

   - 영화 관련 정보가 모두 나열

   ![image](https://user-images.githubusercontent.com/52685242/69307504-2979b780-0c6e-11ea-97ce-04378d583b04.png)

3. ##### 평점 생성

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

4. ##### 평점 삭제

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

5. ##### 영화 좋아요 기능 구현

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

   

