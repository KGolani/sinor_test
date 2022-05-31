from django.http import HttpResponse, JsonResponse
import requests, json, jwt
import datetime

from django.conf import settings


def get_access_token():

    access_data = {
        'imp_key'   : settings.IAMPORT_ACCESS_KEY,
        'imp_secret': settings.IAMPORT_SECRET_KEY,
    }

    url = "https://api.iamport.kr/users/getToken"

    req = requests.post(url, data=access_data)

    access_res = req.json()

    if access_res['code'] == 0:
        return access_res['response']['access_token']
    else:
        return None

def validation_prepare(merchant_id, amount, *args, **kwargs):
    access_token = get_access_token()

    if access_token:
        access_data = {
            'merchant_uid': merchant_id,
            'amount': amount
        }

        url = "https://api.iamport.kr/payments/prepare"

        headers = {
            'Authorization': access_token
        }

        req = requests.post(url, data=access_data, headers=headers)
        res = req.json()

        if res['code'] != 0:
            raise ValueError("API 연결에 문제가 생겼습니다.")
    else:
        raise ValueError("인증 토큰이 없습니다.")

def get_transaction(merchant_id, *args, **kwargs):
    access_token = get_access_token()

    if access_token:
        url = "https://api.iamport.kr/payments/find/" + merchant_id

        headers = {
            'Authorization': access_token
        }

        req = requests.post(url, headers=headers)
        res = req.json()

        if res['code'] == 0:
            context = {
                'imp_id'     : res['response']['imp_uid'],
                'merchant_id': res['response']['merchant_uid'],
                'amount'     : res['response']['amount'],
                'status'     : res['response']['status'],
                'type'       : res['response']['pay_method'],
                'receipt_url': res['response']['receipt_url']
            }
            return context
        else:
            return None
    else:
        raise ValueError("인증 토큰이 없습니다.")



def get_schedule_token():
    data = {
        'imp_key'   : settings.IAMPORT_ACCESS_KEY,
        'imp_secret': settings.IAMPORT_SECRET_KEY,
    }


def coupon_validation(coupon, product):
    if coupon.end_date < datetime.datetime.today():
        return JsonResponse({'message':'Expiration of validity'}, status=401)
    
    if coupon.price >= product.price:
        return JsonResponse({'message' : 'Value error'}, stauts=401)
    return  coupon

def point_validation(point, user, product):
    if user.point - point < 0:
        return JsonResponse({'message':'Not enough point'}, satus=401)
    
    if user.point < point:
        return JsonResponse({'message':'Not enough point'}, satus=401)

    if point >= product.price:
        return JsonResponse({'message' : 'Value error'}, stauts=401)

    return point

def total_price(point, coupon, user, product):
    if int(coupon.price +point) > int(product.price) or int((product.price) - (coupon.price+point)) < 0 :
        return JsonResponse({"message":"ValueError"},status =401)
    
    product_price = (product.price) - (coupon.price+point)

    return product_price