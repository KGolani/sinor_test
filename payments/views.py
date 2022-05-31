import datetime,jwt, json, requests

from django.db.models       import Q
from django.http            import HttpResponse, JsonResponse
from django.shortcuts       import render
from django.views           import View
from django.conf            import settings
from django.db              import transaction

from rest_framework.views      import APIView
from rest_framework.parsers    import JSONParser
from rest_framework.response   import Response

from payments.serializers      import PaymentSerializer
from dateutil.relativedelta    import relativedelta

from users.models           import User
from payments.models        import Coupon, Payment, PaymentTransaction
from products.models        import Product

from utils.login_decorator  import login_decorator, paid_user_decorator
from payments.iamport       import get_access_token, coupon_validation,point_validation,total_price

class ReadyPayment(APIView):
    def get(self, request):
        user = User.objects.get(id = 1)
        return JsonResponse({"point": user.point}, status = 200) # user의 보유 포인트만 return하기위해 작성함 

class PaymentView(APIView):
    @login_decorator
    def post(self,request):
        user = request.user
        
        data = json.loads(request.body)

        # user = User.objects.get(id = data['user']) # test용 로그인 부터 해야하는데 안해서 지정후 사용중
        product = Product.objects.get(name = data['product_name'])
        coupon = Coupon.objects.get(name = data['coupon_name'])
        coupon_validation(coupon, product)
        point = data['point']
        point_validation(point,user,product)
        if int(coupon.price +point) > int(product.price) or int((product.price) - (coupon.price+point)) < 0 :
            return JsonResponse({"message":"ValueError"},status =401)
        
        product_price = total_price(point,coupon,user,product)
    

        user.customer_uid = f"sinor_customer_uid_{user.id}_{data['card_number'][-4:]}"
        user.save()
        bill = {
            "customer_uid":  user.customer_uid,
            "merchant_uid": 'merchant_' + 'sinor_' +str(datetime.datetime.today()),
            "card_number" : data['card_number'],
            "expiry"      : data["expiry"],
            "name"        : product.name,
            "buyer_name"  : user.name if user.name else user.kakao_nickname,
            "buyer_tel"   : user.phone_number,
            'amount'      : float(product_price),
            "birth"       : data['birth'],
            "pwd_2digit"  : data["pwd_2digit"],
        }
        #1회 결제 빌링키 발급 (빌링키는 아이엠포트에 저장) 
        url         = "https://api.iamport.kr/subscribe/payments/onetime"
        header      = {"Authorization":get_access_token(),'Content-Type': 'application/json'}
        data        = json.dumps(bill)
        billing_key         = requests.post(url, headers=header, data=data).json()

        if billing_key['code'] == 1:
            user.point += point
            user.save()
            return JsonResponse({"message":billing_key['message']}, status =401)   

        with transaction.atomic():
            Payment.objects.create(
                user           = user,
                paid_price     = billing_key['response']['amount'],
                used_point     = int(billing_key['response']['amount']) - product.price,
                payment_method = billing_key['response']['pay_method'],
            )

            PaymentTransaction.objects.create(
                user           = user, 
                order_id       = billing_key['response']['merchant_uid'],
                transaction_id = billing_key['response']['imp_uid'],
                amount         = billing_key['response']['amount'],
                success        = True if billing_key['response']['status'] == 'paid' else False,
                type           = billing_key['response']['pay_method']
            )
            sum_time = datetime.datetime.today()+ datetime.timedelta(days=30)

        token_data = {
                "id"        : user.id,
                "start_date": datetime.date.today().strftime('%Y-%m-%d'),
                "end_date"  : sum_time.strftime('%Y-%m-%d'),
                "status"    : billing_key['response']['status'],
                "sendbird_id" : user.sendbird_id
        }

        exp = datetime.datetime.timestamp(sum_time)
        refresh_token = jwt.encode({"data" : token_data, "exp" : exp}, settings.SECRET_KEY, settings.ALGORITHM)
        token         = jwt.encode({"data" : token_data, "exp" : exp}, settings.SECRET_KEY, settings.ALGORITHM)
        user.kakao_refresh_token = refresh_token
        user.point -= point
        user.save()
        return JsonResponse ({"message" : billing_key,"token" : token}, status=200)
       
class SchedulesView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        if data['status'] == 'paid':
            imp_uid      = data['imp_uid']
            url          = f'https://api.iamport.kr/payments/{imp_uid}'
            header       = {"Authorization":get_access_token(),'Content-Type': 'application/json'}
            check_result = requests.get(url, headers=header).json()
           
            user = User.objects.get(Q(name = check_result['response']['buyer_name']) | Q(kakao_nickname = check_result['response']['buyer_name']))
            price = Product.objects.get(name = check_result['response']['name']).price 
            #정기결제 등록 
            url = "https://api.iamport.kr/subscribe/payments/schedule"
            #결제 날짜 설정
            ad, td = datetime.datetime.now(), relativedelta(months=1)
            result_day = td+ad
            schdule_bill = {
                    "customer_uid": check_result['response']['customer_uid'],
                    "schedules"   : [
                    {
                        "merchant_uid": 'merchant_' + 'sinor' +str(datetime.datetime.today()),
                        "schedule_at" : result_day.strftime('%s'),
                        "currency"    : "KRW",
                        "amount"      : float(price),
                        "name"        : check_result['response']['name'],
                        "buyer_name"  : check_result['response']['buyer_name'],
                        "buyer_tel"   : check_result['response']['buyer_tel'],
                    }]
            }
            data = json.dumps(schdule_bill, cls=json.JSONEncoder)
            requests.post(url, headers=header ,data=data)

            ad, td = datetime.datetime.now(), relativedelta(months=1)
            sum_time = td+ad
            token_data = {
                "id"        : user.id,
                "start_date": datetime.date.today().strftime('%Y-%m-%d'),
                "end_date"  : sum_time.strftime('%Y-%m-%d'),
                "status"    : check_result['response']['status'],
                "sendbird_id" : user.sendbird_id
            }
            with transaction.atomic():
                Payment.objects.create(
                user           = user,
                paid_price     = check_result['response']['amount'],
                used_point     = int(check_result['response']['amount']) - Product.objects.get(name = check_result['response']['name']).price,
                payment_method = check_result['response']['pay_method'],
                )
                PaymentTransaction.objects.create(
                    user           = user,
                    order_id       = check_result['response']['merchant_uid'],
                    transaction_id = check_result['response']['imp_uid'],
                    amount         = check_result['response']['amount'],
                    success        = True if check_result['response']['status'] == 'paid' else False,
                    type           = check_result['response']['pay_method']
                )
            exp                = datetime.datetime.timestamp(sum_time)
            refresh_token      = jwt.encode({"data" : token_data, "exp" : exp}, settings.SECRET_KEY, settings.ALGORITHM)
            token              = jwt.encode({"data" : token_data, "exp" : exp}, settings.SECRET_KEY, settings.ALGORITHM)
            user.kakao_refresh_token = refresh_token
            user.save()
            return JsonResponse ({"message" : data ,"token" : token}, status=200)

#스케줄 취소(예약 결제 취소) 
class SchedulesCancleView(APIView): 
    @paid_user_decorator
    def post(self, request): 
        user = request.user

        url    = 'https://api.iamport.kr/subscribe/payments/unschedule'
        header = {"Authorization":get_access_token(),'Content-Type': 'application/json'}
        data   = {
            'customer_uid': user.customer_uid
        }
        coustomer_data = json.dumps(data)
        res            = requests.post(url, headers=header, data=coustomer_data).json()
        
        return JsonResponse({"message":res}, status = 200)