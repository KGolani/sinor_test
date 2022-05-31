import hashlib, random, time
from django.db                import models
from django.db.models.signals import post_save
from utils.time_stamp_models  import TimeStampModel
from users.models             import User
from products.models          import Product

from payments.iamport         import validation_prepare, get_transaction


# 쿠폰과 유저간의 중간 테이블을 만들고 싶음.
class Coupon(models.Model):
    start_date = models.DateTimeField()
    end_date   = models.DateTimeField()
    name       = models.CharField(max_length=45)
    price      = models.DecimalField(max_digits=9, decimal_places=2)

    class Meta:
        db_table = "coupon"


class Payment(TimeStampModel):
    user           = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    paid_price     = models.DecimalField(max_digits=10, decimal_places=2)
    used_point     = models.DecimalField(max_digits=9, decimal_places=2)
    payment_method = models.CharField(max_length=45, null=True)
    product        = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)  # products? 이렇게 변수 이름 바뀔예정.
    is_refunded    = models.BooleanField(default=False)  # 현재 환불은 없음. admin에서 환불 기능 구현.

    class Meta:
        db_table = "payments"


# class PaymentTransactionManager(models.Manager):
#     # 자 트렌잭션 해보자
#     def create_new(self, user, amount, type, success=None, transaction_status=None):
#         if not user:
#             raise ValueError("유저가 확인되지 않았습니다.")

#         short_hash   = hashlib.sha1(str(random.random())).hexdigest()[:2]
#         time_hash    = hashlib.sha1(str(int(time.time()))).hexdigest()[-3:]
#         base         = str(user.email).split('@')[0]
#         key          = hashlib.sha1(short_hash + time_hash + base).hexdigest()[:10]
#         new_order_id = "%s" % (key)

#         # 아임포트 결제 사전 검증
#         validation_prepare(new_order_id, amount)

#         # 트렌젝션 저장
#         new_trans = self.model(
#             user=user,
#             order_id=new_order_id,
#             amount=amount,
#             type=type
#         )

#         if success is not None:
#             new_trans.success            = success
#             new_trans.transaction_status = transaction_status

#         new_trans.save(using=self._db)
#         return new_trans.order_id

#     # 생성된 트랜잭션 검증
#     def validation_trans(self, merchant_id):
#         result = get_transaction(merchant_id)

#         if result['status'] is not 'paid':
#             return result

#         else:
#             return None

#     def all_for_user(self, user):
#         return super(PaymentTransactionManager, self).filter(user=user)

#     def get_recent_user(self, user, num):
#         return super(PaymentTransactionManager, self).filter(user=user)[:num]


'''
order_id는 서버 내에서 자동으로 생성하는 주문 번호이고 
transaction_id는 아임포트에서 생성해주는 고유 번호
'''


class PaymentTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    order_id = models.CharField(max_length=120, unique=True)
    transaction_id = models.CharField(max_length=120, null=True, blank=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    success = models.BooleanField(default=False)
    transaction_status = models.CharField(max_length=220, null=True, blank=True)
    type = models.CharField(max_length=120)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        db_table = 'payment_transaction'

        ordering = ['-created']


# def new_payment_trans_validation(sender, instance, created, *args, **kwargs):
#     if instance.transaction_id:
#         # 거래 후 아임포트에서 넘긴 결과
#         v_trans = PaymentTransaction.objects.validation_trans(
#             merchant_id=instance.order_id
#         )

#         res_merchant_id = v_trans['merchant_id']
#         res_imp_id = v_trans['imp_id']
#         res_amount = v_trans['amount']

#         # 데이터베이스에 실제 결제된 정보가 있는지 체크
#         r_trans = PaymentTransaction.objects.filter(
#             order_id=res_merchant_id,
#             transaction_id=res_imp_id,
#             amount=res_amount
#         ).exists()

#         if not v_trans or not r_trans:
#             raise ValueError('비정상적인 거래입니다.')


# post_save.connect(new_payment_trans_validation, sender=PaymentTransaction)