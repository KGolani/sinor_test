import json
from signal import Handlers
from tkinter import image_names

from rest_framework.response import Response
from rest_framework.views    import APIView

from django.http import JsonResponse
from django.http import HttpResponse, JsonResponse
from users import serializers

from users.models    import User
from payments.models import Coupon
from products.models import Product, Announcement,Event
from .serializers    import ProductTypeSerializer, CouponSerializer,AnnouncementSerializer, EventSerializer
from utils.s3 import S3_Client,FileHandler

from django.conf import settings

s3client = S3_Client(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_STORAGE_BUCKET_NAME, settings.AWS_REGION)

#web
class ProductView(APIView):
    #상품등록
    def post(self,request):
        try:
            serializer = ProductTypeSerializer(data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status = 400)
#상품 조회
    def get (self, request):
        data = Product.objects.all()
        serializer = ProductTypeSerializer(data, many=True)
        return Response(serializer.data)

#상품삭제
    def delete(self, request):
        data = json.loads(request.body)
        product = Product.objects.get(name=data['name'])
        product.delete()
        product.save()
        return HttpResponse(200)

# #web
class PointView(APIView):
#포인트 생성
    def post(self, request):
        data = json.loads(request.body)
        user = User.objects.get(id = data["user_id"])
        user.point += data["point"]
        user = user.save()
        return HttpResponse(200)
# 포인트 조회
    def get(self, request):
        queryset = User.objects.all()
        result = [{
            "name" : user.name,
            "gender"  : "남자" if user.gender == 0 else "여자",
            "birth_date" : user.birth_date,
            "point" : user.point
        }for user in queryset]
        return JsonResponse({"result":result}, status = 200)
#web
class CouponView(APIView):
#쿠폰 생성
    def post(self,request):
        serializer = CouponSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(201)
#쿠폰 조회
    def get(self, request):
        data = Coupon.objects.all()
        serializer = CouponSerializer(data, many =True)
        return Response({"result" : serializer.data}, status = 200)
#쿠폰 삭제
    def delete(self, request):
        data = json.loads(request.body)
        coupon = Coupon.objects.get(name = data["name"])
        coupon.delete()
        coupon.save()
        return HttpResponse(200)

#공지사항
class NoticeView(APIView):
    def post(sef, request):
        serializer = AnnouncementSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    def patch(self, request):
        data = request.data
        target = Announcement.objects.get(id=data['id'])
        serializer = AnnouncementSerializer(target,data = data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)
    
    def get(self, request):
        data = Announcement.objects.all()
        serializer = AnnouncementSerializer(data, many =True)
        return Response({"result" : serializer.data}, status = 200)
    
    def delete(self,request):
        data = request.data
        target = Announcement.objects.get(id = data['id'])
        target.delete()
        target.save()
        return HttpResponse(200)
#이벤트
class EventView(APIView):
    #이벤트 생성
    def post(self, request):
        data = request.data
        images  = request.FILES.get('images', None)
        s3control  = FileHandler(s3client)
        image_url = s3control.upload(directory='event', file=images)
        Event.objects.create(
            title       = data['title'],
            content     = data['content'],
            image_url   = image_url,
            sequence    = data['sequence'],
            randing_link= data['randing_link'],
            start_date  = data['start_date'],
            end_date    = data['end_date'],
            status      = data['status']
        )
        return HttpResponse("Success",status=201)
    def patch(self, request):
        data = request.data
        target = Event.objects.get(id=data['id'])
        serializer = AnnouncementSerializer(target,data = data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)
    #조회
    def get(self,request):
        data = Event.objects.all()
        serializer = EventSerializer(data, many =True)
        return Response({"result" : serializer.data}, status = 200)

    #삭제
    def delete(self, request):
        event = Event.objects.get(id = request.data['id'])        
        image = event.image_url
        img = image[image.find('event'):]
        s3client.delete(bucket_name='sinor', image_name=img)
        event.delete()

        return HttpResponse(status =200)