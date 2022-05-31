from enum import unique
from django.db               import models
from utils.time_stamp_models import TimeStampModel

class User(TimeStampModel):
    unique_id               = models.CharField(max_length=254, unique=True)
    sendbird_id             = models.CharField(max_length=400, blank=True)  # 필요함
    customer_uid            = models.CharField(max_length=400, blank=True)  # 필요함. sinor_customer_uid_{user.id}_{data}
    phone_number            = models.CharField(max_length=20, blank=True)   # 필요함.
    name                    = models.CharField(max_length=40, blank=True)   # 필요함.
    gender                  = models.SmallIntegerField(null=True)           # 1번 남자, 2번 여자
    birth_year              = models.IntegerField(null=True)
    birth_date              = models.CharField(max_length=20, blank=True)
    point                   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reported_count          = models.IntegerField(default=0)
    is_deleted              = models.BooleanField(default=False)            # is_deleted=True 유저가 보이면 안된다. 데코레이터 혹은 matchintview의 Q객체에 is_delete False로 필터
    deleted_at              = models.DateTimeField(null=True)               # 회원 탈퇴시, today.time으로 지정.
    refresh_token           = models.CharField(max_length=300, blank=True)  # 원래는 카카오 리프레쉬 토큰 -> 리프레쉬 토큰으로 변수명 바꿈.
                                                                            # 결제하고 생성되는 token : payments의 token_data가 payload 들어갑니다.
    kakao_id                = models.CharField(max_length=50, blank=True)
    kakao_nickname          = models.CharField(max_length=50, blank=True)

    # adminUser 테이블을 따로 만들지, user에서 필드를 1,0으로 줄지 결정

    class Meta:
        db_table = 'users'

# 종교
class Religion(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        db_table = 'religions'

# 주량
class DrinkCapacity(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        db_table = 'drink_capacities'

# 솔로 이유
class SoloReason(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        db_table = 'solo_reasons'

# 체형
class Physical(models.Model):
    shape = models.CharField(max_length=30)

    class Meta:
        db_table = 'physicals'

# 직업
class Job(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        db_table = "jobs"

# 유저 프로필 이미지
class UserImage(models.Model):
    sequence    = models.IntegerField()
    url         = models.URLField(max_length=400)
    user        = models.ForeignKey("User", on_delete=models.CASCADE)

    class Meta:
        db_table = "user_images"

class UserProfile(models.Model):
    introduce      = models.TextField()
    height         = models.DecimalField(max_digits=5 , decimal_places=2)
    user           = models.ForeignKey("User", on_delete=models.CASCADE)
    religion       = models.ForeignKey("Religion", on_delete=models.SET_NULL, null=True)
    drink_capacity = models.ForeignKey("DrinkCapacity", on_delete=models.SET_NULL, null=True)
    solo_reason    = models.ForeignKey("SoloReason", on_delete=models.SET_NULL, null=True)
    physical       = models.ForeignKey("Physical", on_delete=models.SET_NULL, null=True)
    job            = models.ForeignKey("Job", on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'user_profiles'

# 이거 사용 여부 모르겠음.
class Term(models.Model):
    title    = models.CharField(max_length=100)
    contents = models.URLField(max_length=400)

    class Meta:
        db_table = 'terms'

# 핸드폰 로그인 건드리면 안됨.
class AuthenticationNumber(models.Model):
    phone_number  = models.CharField(max_length=30)
    certification = models.IntegerField()

    class Meta:
        db_table = "authentication_numbers"




