from django.db import models
from utils.time_stamp_models import TimeStampModel

class Thema(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "themas"

class Product(TimeStampModel): # 이름변경: ProductType -> Products 로 변경
    name         = models.CharField(max_length=20)
    period       = models.IntegerField()
    price        = models.DecimalField(max_digits=9, decimal_places=2)
    thema        = models.ForeignKey("Thema", on_delete=models.CASCADE, null= True)
    running_date = models.DateField(null=True)
    image        = models.ForeignKey("ProductImage", on_delete=models.CASCADE, null=True)
    location     = models.CharField(max_length=200,null=True)
    explanation  = models.TextField(null=True)
    prepare      = models.CharField(max_length=200,null=True)
    caution      = models.TextField(null=True)
    host_company = models.CharField(max_length=200,null=True)
    image        = models.ForeignKey("ProductImage", on_delete=models.CASCADE, null=True)
    
    class Meta:
        db_table = "products" # 이름변경: product_types -> products

class ProductImage(models.Model):
    product_image = models.CharField(max_length=200)

    class Meta:
        db_table = "product_image"

# 공지사항 : admin용
class Announcement(TimeStampModel):
    title        = models.CharField(max_length=200)
    content      = models.TextField()
    status       = models.BooleanField(default=False)
    popup_status = models.BooleanField(default=False)

    class Meta: 
        db_table = "announcements"

# event : admin용
class Event(TimeStampModel):
    title        = models.CharField(max_length=200)
    content      = models.TextField()
    image_url    = models.CharField(max_length=200)
    sequence     = models.IntegerField()
    randing_link = models.CharField(max_length=200, null=True)
    start_date   = models.DateField()
    end_date     = models.DateField()
    status       = models.BooleanField(default=False)

    class Meta:
        db_table = 'events'
