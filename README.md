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

   ![image](https://user-images.githubusercontent.com/52685242/69307560-56c66580-0c6e-11ea-9805-02cf02ca9620.png)

4. ##### 평점 삭제

   - 영화 평점 삭제는 본인만 가능
   - 데이터베이스에서 삭제되면, 해당하는 영화의 `영화 상세보기` 페이지로 Redirect 합니다.

   ![image](https://user-images.githubusercontent.com/52685242/69307657-a0af4b80-0c6e-11ea-80b9-da360d8eccce.png)

5. ##### 영화 좋아요 기능 구현

   - 좋아하는 영화를 담아 놓을 수 있도록 구현
   - 로그인 한 유저만 해당 기능을 사용 가능

   ![image](https://user-images.githubusercontent.com/52685242/69311744-71014300-0c70-11ea-8881-a037942351fc.png)

   