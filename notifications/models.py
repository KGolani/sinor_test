from django.db               import models
from utils.time_stamp_models import TimeStampModel
from users.models            import User

class Notification(TimeStampModel):
    url          = models.URLField(max_length=400)
    is_clicked   = models.BooleanField(default=False)
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name="noti_user_set")
    send_user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="noti_send_user_set")

    class Meta:
        db_table = "notifications"

class NotificationInformation(models.Model):
    category  = models.CharField(max_length=20)
    message   = models.CharField(max_length=100)
    image_url = models.URLField(max_length=400)

    class Meat:
        db_table = "notification_informations"
