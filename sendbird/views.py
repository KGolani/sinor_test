import json, requests

from datetime                import datetime
from django.http             import JsonResponse
from rest_framework.views    import APIView

from my_settings             import sendbird_master_token, sendbird_application_id
from pairs.models            import Wishlist
from sendbird.models         import SendbirdChannel, SendbirdChannelUser, SendbirdReport, MatchingRate
from users.models            import User

# sendbird API 클래스
class SendbirdAPI():
    def __init__(self):
        self.master_token   = sendbird_master_token
        self.application_id = sendbird_application_id
        self.base_url       = f'https://api-{self.application_id}.sendbird.com'

    def get_sendbird_user(self, user_id):
        try:
            headers = {'Api-Token': f'{self.master_token}'}
            # user 정보를 가져옵니다. requests.get !!!
            return requests.get(
                f"{self.base_url}/v3/users/{user_id}",
                headers=headers,
                timeout=3
            )
        # 지연으로 인해, timeout 예외가 발생할 경우, 처리
        except requests.exceptions.Timeout:
            return JsonResponse({"message": "sendbird_time_out_error"}, status=400)

    # sendbird의 Month Active User(MAU) 값을 가져옵니다.
    def get_sendbird_mau(self):
        try:
            headers = {'Api-Token': f'{self.master_token}'}
            query   = {"date":datetime.today().strftime("%Y-%m-%d")}
            return requests.get(
                f'{self.base_url}/v3/applications/mau',
                query,
                headers=headers,
                timeout=3
            )

        except requests.exceptions.Timeout:
            return JsonResponse({"message": "sendbird_time_out_error"}, status=400)

    # sendbird의 Daily Active User(DAU) 값을 가져옵니다.
    def get_sendbird_dau(self):
        try:
            headers = {'Api-Token': f'{self.master_token}'}
            query   = {"date": datetime.today().strftime("%Y-%m-%d")}
            return requests.get(
                f'{self.base_url}/v3/applications/dau',
                query,
                headers=headers,
                timeout=3
            )

        except requests.exceptions.Timeout:
            return JsonResponse({"message": "sendbird_time_out_error"}, status=400)

    # Webhook 열려있는 기능 목록 조회.
    # 현재는 user:report(신고), group_channel:join(유저 채팅방 입장) group_channel:leave (채팅방 나가기)
    def get_sendbird_webhook_categories(self):
        try:
            headers = {'Api-Token': f'{self.master_token}'}
            query   = {"display_all_webhook_categories": "true"}
            return requests.get(
                f'{self.base_url}/v3/applications/settings/webhook',
                query,
                headers=headers,
                timeout=3
            )

        except requests.exceptions.Timeout:
            return JsonResponse({"message": "sendbird_time_out_error"}, status=400)

    # 서버에서 channel을 만들어야 할 때, 사용.
    def create_sendbird_channel(self, user_ids):
        try:
            headers = {'Api-Token': f'{self.master_token}'}
            body={
                "user_ids": user_ids,
                "is_distinct": True
            }
            return requests.post(
                f"{self.base_url}/v3/group_channels",
                headers=headers,
                json=body,
                timeout=3
            )

        except requests.exceptions.Timeout:
            return JsonResponse({"message": "sendbird_time_out_error"}, status=400)

    # 서버에서 sendbird user를 만들어야 할 때, 사용.
    def create_sendbird_user(self, user_id, nickname):
        try:
            headers = {'Api-Token': f'{self.master_token}'}
            data = {
                "user_id": f"{user_id}",
                "nickname": f"{nickname}",
                "profile_url": "https://sendbird.com/main/img/profiles/profile_05_512px.png",
            }

            return requests.post(
                f"https://api-{self.application_id}.sendbird.com/v3/users",
                headers=headers,
                json=data,
                timeout=3
            )

        except requests.exceptions.Timeout:
            return JsonResponse({"message": "sendbird_time_out_error"}, status=400)

    # 서버에서 user 신고 할 때, 사용. 테스트용.
    # 신고자 sendbird_id, 욕설한 유저 sendbird_id, 신고내용, 신고 종류(spam 등등), 신고가 발생한 sendbird channel_url
    def report_sendbird_user(self, reporting_user_id, offending_user_id , description, report_category, channel_url):
        try:
            headers = {'Api-Token': f'{self.master_token}'}
            body = {
                "channel_type"       : "group_channels",
                "channel_url"        : f"{channel_url}",
                "report_category"    : f"{report_category}",
                "reporting_user_id"  : f"{reporting_user_id}",
                "report_description" : f"{description}"
            }
            return requests.post(
                f"{self.base_url}/v3/report/users/{offending_user_id}",
                headers=headers,
                json=body,
                timeout=3
            )

        except requests.exceptions.Timeout:
            return JsonResponse({'message': "sendbird_time_out_error"}, status=400)

class SendbirdMAUView(APIView):
    def get(self, request):
        response = SendbirdAPI().get_sendbird_mau()
        return JsonResponse({'message': 'success', 'response': response.json()}, status=200)

class SendbirdDAUView(APIView):
    def get(self, request):
        response = SendbirdAPI().get_sendbird_dau()
        return JsonResponse({'message': 'success', 'response': response.json()}, status=200)

class SendbirdWebhookCategoriesView(APIView):
    def get(self, request):
        response = SendbirdAPI().get_sendbird_webhook_categories()
        return JsonResponse({'message': 'success', 'response': response.json()}, status=200)

class SendbirdWebhookView(APIView):
    def post(self, request):
        try:
            data     = json.loads(request.body) # sendbird 에서 들어온 webhook 데이터를 받음.
            category = data['category']         # sendbird webhook 데이터 종류 파악.

            if category == 'group_channel:join': # 채팅방이 만들어 지는 webhook이면 실행.
                host_user  = User.objects.get(sendbird_id=data['users'][0]['user_id']) # channel 생성 시, moderation, operator 없음!
                guest_user = User.objects.get(sendbird_id=data['users'][1]['user_id']) # user가 배열로 들어오므로 작성.

                # 새로운 channel이면 생성, 기존에 channel이 있다면 가져오기.
                channel, is_created = SendbirdChannel.objects.get_or_create(
                    channel_url = data['channel']['channel_url']
                )
                if is_created: # 기존에 있는 channel이면, DB에 해당 channel 방의 user 저장.
                    SendbirdChannelUser.objects.create(
                        sendbird_channels_id   = channel.pk,
                        sendbird_host_user_id  = host_user.pk,
                        sendbird_guest_user_id = guest_user.pk
                    )
                # 채팅방이 만들어지면, 매칭률 계산을 위한 DB 레코드 저장.
                # 매칭률 = 채팅방 생성개수/찜보내기 개수
                MatchingRate.objects.create(
                    sendbird_channel_user = channel.sendbirdchanneluser_set.get(sendbird_channels_id=channel.pk),
                    wishlist              = Wishlist.objects.get(user_id=host_user.pk, liked_user_id=guest_user.pk)
                )

            # 소프트 딜리트
            # channel을 떠날 때, sendbird의 Response에서 뒤에 & 붙어서 옴..
            if category == 'group_channel:leave':
                channel_url     = data['channel']['channel_url']
                channel         = SendbirdChannel.objects.get(channel_url=channel_url[:channel_url.find('&')])
                channel.delete()

            if category == 'user:report':  # 유저 신고 발생.
                SendbirdReport.objects.create(
                    reason                = data['report_description'],
                    reporter_sendbird_id  = data['reporting_user']['user_id'],
                    offending_sendbird_id = data['offending_user']['user_id'],
                    sendbird_channels     = data['channel']['channel_url']
                )
                # 유저 신고 발생 시, user 테이블의 reported_count + 1 -> 인기도랑 연관되어 있음.
                offending_user = User.objects.get(sendbird_id=data['offending_user']['user_id'])
                offending_user.reported_count += 1
                offending_user.save()

            return JsonResponse({'message': 'success'}, status=200)

        except KeyError:
            return JsonResponse({'message': 'key_error'}, status=400)
        except SendbirdChannel.DoesNotExist:
            return JsonResponse({'message': 'sendbird_channel_not_exist'}, status=400)

class SendbirdReportView(APIView): # 일부러 신고내기위한 용도
    def post(self, request):
        data = json.loads(request.body)

        reporting_user_id = data["reporting_user_id"]
        offending_user_id = data["offending_user_id"]
        description       = data["description"]
        report_category   = data["report_category"]
        channel_url       = data["channel_url"]

        SendbirdAPI().report_sendbird_user(
            reporting_user_id = reporting_user_id,
            offending_user_id = offending_user_id,
            description       = description,
            report_category   = report_category,
            channel_url       = channel_url
        )

        return JsonResponse({"message": "report"}, status=200)
        