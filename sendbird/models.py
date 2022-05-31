from django.db               import models
from utils.time_stamp_models import TimeStampModel
from users.models            import User
from pairs.models            import Wishlist, Interest

class SendbirdChannelUser(models.Model):
    sendbird_host_user  = models.ForeignKey("users.User", max_length=400, on_delete=models.CASCADE, related_name='host_user')
    sendbird_guest_user = models.ForeignKey("users.User", max_length=400, on_delete=models.CASCADE, related_name='guest_user')
    sendbird_channels   = models.ForeignKey("SendbirdChannel", on_delete=models.CASCADE)

    class Meta:
        db_table = 'sendbird_channel_users'

class SendbirdChannel(TimeStampModel):
    channel_url = models.URLField(max_length=400)
    is_deleted  = models.BooleanField(default=False)

    class Meta:
        db_table = 'sendbird_channels'

class SendbirdReport(TimeStampModel):
    reason                     = models.CharField(max_length=300, blank=True)
    reporter_sendbird_id       = models.CharField(max_length=100)
    offending_sendbird_id      = models.CharField(max_length=100)
    sendbird_channels          = models.URLField(max_length=400)

    class Meta:
        db_table = 'sendbird_reports'

class MatchingRate(models.Model):
    sendbird_channel_user = models.ForeignKey("SendbirdChannelUser", on_delete=models.CASCADE)
    wishlist              = models.ForeignKey("pairs.Wishlist", on_delete=models.CASCADE)

    class Meta:
        db_table = 'matching_rates'

class Recommendation(models.Model):
    interests = models.ForeignKey("pairs.Interest", on_delete=models.CASCADE)
    content   = models.CharField(max_length=400)

    class Meta:
        db_table = 'recommendations'