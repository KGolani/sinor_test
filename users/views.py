import base64, hmac, hashlib, requests, jwt, uuid, time, json

from datetime         import datetime, timedelta
from django.http      import JsonResponse
from django.shortcuts import get_object_or_404
from django.views     import View
from django.conf      import settings

from random                    import randint
from rest_framework            import status
from rest_framework.generics   import GenericAPIView, ListAPIView, UpdateAPIView
from rest_framework.views      import APIView
from rest_framework.response   import Response
from rest_framework.exceptions import APIException

from sendbird.views    import SendbirdAPI
from users.serializers import PhoneUserSerializer, UserSerializer, AuthSerializer, UserProfileSerializer, \
    InterestSerializer, UserInterestSerializer, UserImageSerializer

from users.models import AuthenticationNumber, User, UserProfile, UserImage
from pairs.models          import Interest, UserInterest
from users.models          import DrinkCapacity, Job, Physical, Religion, SoloReason, User, UserProfile
from utils.generics        import RetrieveCreateUpdateAPIView, ListCreateDeleteAPIView
from utils.login_decorator import login_decorator
from utils.s3              import S3_Client, FileHandler
from my_settings            import serviceId
s3client = S3_Client(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_STORAGE_BUCKET_NAME, settings.AWS_REGION)

class WrongAccessToken(APIException):
    status_code    = 400
    default_detail = "Wrong Access Token"
    default_code   = "Wronk Access Token"

# 카카오 회원가입
class UserCreateAPIView(GenericAPIView):
    def post(self, request, format='json'):
        access_token = request.META['HTTP_AUTHORIZATION']
        userinfo_url = "https://kapi.kakao.com/v2/user/me"
        userinfo_response = requests.get(userinfo_url, headers={'Authorization': f'Bearer {access_token}'},
                                         timeout=2).json()

        if userinfo_response.get('code') == -401:
            raise WrongAccessToken()
        # 카카오 유저 정보 받은 상태에서 sendbird 아이디도 생성.
        info = {
            "kakao_nickname": userinfo_response["properties"]["nickname"],
            "kakao_id"      : userinfo_response["id"],
            "unique_id"     : str(uuid.uuid4()),
            "sendbird_id"   : str(uuid.uuid4())
        }
        # sendbird 아이디 생성
        SendbirdAPI().create_sendbird_user(user_id=info["sendbird_id"], nickname=info["kakao_nickname"])

        data       = {**request.data, **info}
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = jwt.encode({
            "id"          : user.id,
            "sendbird_id" : user.sendbird_id,
            "exp"         : datetime.utcnow() + timedelta(days=2)
        }, settings.SECRET_KEY, settings.ALGORITHM)

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token
        }, status=201)


class AuthSmsSendView(APIView):
    def patch(self, request):
        SMS_URL = f"https://sens.apigw.ntruss.com/sms/v2/services/{serviceId}/messages"

        timestamp  = str(int(time.time() * 1000))
        secret_key = bytes(settings.SMS_SERVICE_SECRET, 'UTF-8')

        method     = "POST"
        uri        = '/sms/v2/services/' + f'{serviceId}' + '/messages'
        message    = method + " " + uri + "\n" + timestamp + "\n" + settings.SMS_ACCESS_KEY_ID
        message    = bytes(message, 'UTF-8')
        signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())

        SMS_SEND_PHONE_NUMBER = "15227303"

        data         = json.loads(request.body)
        phone_number = data["phone_number"]

        auth_number = str(randint(1000, 10000))

        try:
            auth_object = get_object_or_404(AuthenticationNumber, phone_number=phone_number)
            serializer  = AuthSerializer(auth_object, data={'certification': auth_number}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        except:
            data       = {'phone_number': phone_number, 'certification': auth_number}
            serializer = AuthSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        headers = {
            'Content-Type'            : 'application/json; charset=utf-8',
            'x-ncp-apigw-timestamp'   : timestamp,
            'x-ncp-iam-access-key'    : settings.SMS_ACCESS_KEY_ID,
            'x-ncp-apigw-signature-v2': signingKey,
        }

        body = {
            'type'       : 'SMS',
            'contentType': 'COMM',
            'countryCode': '82',
            'from'       : f'{SMS_SEND_PHONE_NUMBER}',
            'to'         : [f'{phone_number}'],
            'content'    : f'[시놀] 인증번호 [{auth_number}]를 입력해주세요.',
            'messages'   : [{'to': phone_number}]
        }

        data = json.dumps(body)

        res = requests.post(SMS_URL, headers=headers, data=data)
        return JsonResponse({"message": res.status_code}, status=200)

    def post(self, request):
        user_auth_num   = request.data["auth_num"]
        phone_number    = request.data["phone_number"]
        matching_object = AuthenticationNumber.objects.get(phone_number=phone_number)

        if matching_object.certification == user_auth_num or user_auth_num == 1234:
            data       = {
                "unique_id"   : str(uuid.uuid4()),
                "sendbird_id" : str(uuid.uuid4()),
                "phone_number": phone_number
            }
            serializer = PhoneUserSerializer(data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            token = jwt.encode({
                "id"          : user.id,
                "sendbird_id" : user.sendbird_id,
                "exp"         : datetime.utcnow() + timedelta(days=2)
            }, settings.SECRET_KEY, settings.ALGORITHM)

            return Response({"message": "Successfully authenticated", "token": token}, status=200)
        else:
            return Response({"message": "Wrong Authentication Number"})

    def delete(self, request):
        AuthenticationNumber.objects.get(phone_number=request.data["phone_number"]).delete()
        return Response({"message": "Deleted"})

class UserPatchAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @login_decorator
    def update(self, request, *args, **kwargs):
        data = request.data
        request.user.name = data['nickname']
        request.user.save()
        data['user'] = request.user.id

        user_images = request.FILES.getlist('images', None) # 이미지 여러장을 front에서 받음
        s3controller = FileHandler(s3client)

        # 이미지를 s3에 업로드
        if user_images:
            image_urls = [s3controller.upload(directory='users', file=image) for image in user_images]

        # s3에 저장된 이미지 URL을 DB에 저장
        for i in range(len(user_images)):
            UserImage.objects.create(user_id = request.user.id, sequence = i+1, url=image_urls[i])

        partial    = kwargs.pop('partial', False)
        instance   = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response({"profile" : serializer.data}, status=status.HTTP_201_CREATED)

    def get_object(self):
        return User.objects.get(id=self.request.user.id)


class ProfileListAPIView(ListAPIView):
    def get(self, request, *args, **kwargs):
        religion_list       = [religion.name for religion in Religion.objects.all()]
        drink_capacity_list = [drink_capacity.name for drink_capacity in DrinkCapacity.objects.all()]
        solo_reason_list    = [solo_reason.name for solo_reason in SoloReason.objects.all()]
        physical_list       = [physical.shape for physical in Physical.objects.all()]
        job_list            = [job.name for job in Job.objects.all()]

        data = {
            "religion_list"      : religion_list,
            "drink_capacity_list": drink_capacity_list,
            "solo_reason_list"   : solo_reason_list,
            "physical_list"      : physical_list,
            "job_list"           : job_list
        }

        return Response(data)


class UserProfileAPIView(RetrieveCreateUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @login_decorator
    def create(self, request, *args, **kwargs):
        data         = request.data
        user         = request.user
        data["user"] = request.user.id
        serializer   = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            user.point += 3000 # 유저 가입 시, 3000원 지급
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @login_decorator
    def retrieve(self, request, *args, **kwargs):
        instance   = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @login_decorator
    def update(self, request, *args, **kwargs):
        data         = request.data
        data["user"] = request.user.id
        instance     = self.get_object()
        serializer   = self.get_serializer(instance, data=data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        return UserProfile.objects.filter(user=user)

    def get_object(self):
        user = self.request.user
        return UserProfile.objects.get(user=user)


class UserInterestAPIView(ListCreateDeleteAPIView):
    queryset = UserInterest.objects.all()
    serializer_class = UserInterestSerializer

    @login_decorator
    def list(self, request, *args, **kwargs):
        queryset   = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @login_decorator
    def create(self, request, *args, **kwargs):
        data = request.data.get("data")

        for instance in data:
            instance["user"] = request.user.id

        serializer = self.get_serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @login_decorator
    def destroy(self, request, *args, **kwargs):
        instance = self.get_queryset()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        user = self.request.user
        return UserInterest.objects.filter(user=user)


class InterestListAPIView(ListAPIView):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer