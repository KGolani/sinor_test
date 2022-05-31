from cgi import test
from decimal                 import Decimal
from datetime                import datetime
import json
from re import X
from urllib import response
import model

from rest_framework.views    import APIView
from rest_framework.response import Response

from django.db.models        import Q,Prefetch,Count
from django.http             import JsonResponse

from sendbird.views          import SendbirdAPI
from users.models            import User
from .serializers            import LocationSerializer, UserSerializer, WishListSerializer, FilterUserSerializer, InterestTestSerializer
from .models                 import BlockList, Location, UserInterest, Wishlist
from utils.login_decorator   import login_decorator
from model.model             import recommendation

class LocationView(APIView):
    def get_object(self, request):
        try:
            return Location.objects.get(user_id = request)

        except Location.DoesNotExist:
            return Response({'message' : 'INVALID_USER'}, status = 400)

    @login_decorator
    def get(self, request):
        user_location = self.get_object(request.user.id)
        serializer = LocationSerializer(user_location)

        return Response(serializer.data, status = 200)

    @login_decorator
    def patch(self, request, format=None):
        request.data['user'] = request.user.id

        location   = self.get_object(request.user.id)
        serializer = LocationSerializer(location, data = request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({'message' : 'SUCCESS'} ,status = 200)

        return Response(f'message : {serializer.errors}', status = 400)

    @login_decorator
    def post(self, request, format=None):
        if not Location.objects.filter(user_id = request.user.id).exists():
            request.data['user'] = request.user.id

            serializer = LocationSerializer(data = request.data)

            if serializer.is_valid():
                serializer.save()

                return Response({'message' : 'SUCCESS'} ,status = 201)

            return Response(serializer.errors, status = 400)

        else:
            return Response({'message' : 'EXIST_USER'}, status = 400)

class MatchingView(APIView):
    @login_decorator
    def get(self, request):
        try:
            user = User.objects.prefetch_related(Prefetch('location_set'),
                                                 Prefetch(
                                                     'blocker_set',queryset=BlockList.objects.select_related('user')
                                                 ),
                                                 Prefetch(
                                                     'from_user_set',queryset=Wishlist.objects.select_related('user')
                                                 )).get(id = request.user.id)

            user_location    = user.location_set.get(user_id = request.user.id)
            max_distance     = Decimal(request.query_params.get('distance', user_location.max_distance))
            min_age,max_age  = int(request.query_params.get('min_age',50)),int(request.query_params.get('max_age', 100))

            block_list = [blocked_user.blocked_user.id for blocked_user in user.blocker_set.all()]
            wish_list  = [wish_user.liked_user.id for wish_user in user.from_user_set.all()]

            q = Q(is_deleted = 1) # 회원인 user들만 보이게 함.

            q &= Q(location__latitude__lte = user_location.latitude + (Decimal(0.01)*max_distance))

            q &= Q(location__longtitude__lte = user_location.longtitude + (Decimal(0.015)*max_distance))

            q &= ~Q(id__in = block_list)

            q &= ~Q(id__in = wish_list)

            if max_age:
                q &= Q(birth_year__gte = datetime.today().year - min_age) & Q(birth_year__lte = datetime.today().year - max_age)

            if user.gender == 1:
                q &= Q(gender = 2)

            if user.gender == 2:
                q &= Q(gender = 1)

            matching_list = User.objects.annotate(like_count=Count('to_user_set__liked_user'))\
                                        .filter(q).order_by('-like_count').exclude(id = request.user.id)

            serializer = UserSerializer(matching_list, many=True)

            return Response(serializer.data, status = 200)

        except Location.DoesNotExist:
            return Response({'message' : 'INVALID_USER'}, status = 400)

    @login_decorator
    def post(self, request):
        user_id = request.user.id
        #user_id = 1 #  test 용 hardcording
        if not Wishlist.objects.filter(user_id = user_id, liked_user_id = request.data['liked_user']).exists():
            request.data['user'] = user_id

            serializer = WishListSerializer(data = request.data)

            if request.data['liked_user'] == user_id:
                return Response({'message' : 'KEY_ERROR'}, status = 400)

            if serializer.is_valid():
                serializer.save()

        if Wishlist.objects.filter(user_id=request.data['liked_user'], liked_user_id=user_id).exists():
            host = User.objects.get(id=user_id)
            guest = User.objects.get(id=request.data['liked_user'])

            # 이 부분 FE에서 일어남. 테스트 위해서 일부러 작성해놓음.
            # SendbirdAPI().create_sendbird_user(user_id=host.sendbird_id, nickname=host.name)
            # SendbirdAPI().create_sendbird_user(user_id=guest.sendbird_id, nickname=guest.name)
            #
            # SendbirdAPI().create_sendbird_channel([host.sendbird_id, guest.sendbird_id])

            return Response({
                'message': '대화를 시작해보세요.',
                'host' : FilterUserSerializer(host).data,
                'guest': FilterUserSerializer(guest).data
            }, status=200)

        return Response({"message": "SUCCESS"}, status=200)

    @login_decorator
    def delete(self, request):
        try:
            user_id  = request.user.id
            wishlist = Wishlist.objects.get(user_id = user_id, liked_user_id = request.data.get('liked_user', None))
            wishlist.delete()

            return Response({'message' : 'DELETE'}, status = 204)

        except Wishlist.DoesNotExist:
            return Response({'message' : 'INVALIDE_USER'}, status = 400)

class MetoYou(APIView):
    @login_decorator
    def get(self, request):
        user_id = request.user.id

        wish_users = Wishlist.objects.filter(user_id=user_id)
        mylike_ids = [wish.liked_user_id for wish in wish_users]
        mylike_users = User.objects.filter(id__in=mylike_ids)

        serializer = FilterUserSerializer(mylike_users, many=True)

        return Response(serializer.data, status=200)

class YoutoMe(APIView):
    @login_decorator
    def get(self, request):
        user_id = request.user.id

        wish_users = Wishlist.objects.filter(liked_user_id=user_id)
        youlike_ids = [wish.user_id for wish in wish_users]
        youlike_users = User.objects.filter(id__in=youlike_ids)

        serializer = FilterUserSerializer(youlike_users, many=True)

        return Response(serializer.data, status=200)

class TestView(APIView):
    def get(self, request):
        model = recommendation()
        users = UserInterest.objects.all()
        # users = User.objects.prefetch_related('user_interest')
        # serializer = InterestTestSerializer(user, many=True)
        # test_li = []
        # for user in users:
        #     user_id = user.user_id
        #     test_li = [[
        #         user_id,[i.interest_id for i in users.filter(user_id=user_id)]
        #     ]]
        test_li = []
        for user in users:
            test_li.append([user.user_id,[str(i.interest_id) for i in users.filter(user_id=user.user_id)]])
        # for i in users:
        model.get_embedding_matrix('embedding(wiki).json', 300)
        model.fit(test_li, n_cluster=3)
        x = model.predict(2)
        
        # result = model.fit(test_li, n_cluster=3)
        # y = model.predict(2)
        return Response(x, status=200)