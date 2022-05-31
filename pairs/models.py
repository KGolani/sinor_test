from django.db import models
from users.models import User

# 지도: 위도 경도
class Location(models.Model):
    longtitude   = models.DecimalField(max_digits=9, decimal_places=6)
    latitude     = models.DecimalField(max_digits=9, decimal_places=6)
    max_distance = models.IntegerField(default=0)
    user         = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "locations"


# 관심사 필요함.
class Interest(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        db_table = "interests"


# 각각의 유저마다 관심사 저장. 필요함.
class UserInterest(models.Model):
    sequence = models.IntegerField()
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    interest = models.ForeignKey("Interest", on_delete=models.CASCADE)

    class Meta:
        db_table = "user_interests"


# 과격한 언행. 필요함.
class BannedWord(models.Model):
    word = models.CharField(max_length=20)

    class Meta:
        db_table = "banned_words"


# 서로 찜할때, 필요함.
class Wishlist(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user_set")
    liked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="to_user_set")

    class Meta:
        db_table = "wishlists"


# 연락처 차단 + 신고 -> 1번 2,3번 블락 시, 4,5,6번 보여야 함.
class BlockList(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocker_set")
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_set")

    class Meta:
        db_table = "blocklists"