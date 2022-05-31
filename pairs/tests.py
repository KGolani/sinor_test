import jwt, json

from django.test import TestCase, Client

from sinor_Server.settings import SECRET_KEY, ALGORITHM
from users.models import User
from .models import Wishlist, Location


class LocationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.bulk_create([
            User(
                id=1,
                unique_id='1',
                phone_number='01011112222',
                name='김팔봉',
                gender=1,
                birth_year=1960,
                birth_date='0101',
                point=3000,
                reported_count=0,
                is_deleted=1,
            ),
            User(
                id=2,
                unique_id='2',
                phone_number='01033334444',
                name='조봉팔',
                gender=1,
                birth_year=1958,
                birth_date='0101',
                point=3000,
                reported_count=0,
                is_deleted=1,
            ),
            User(
                id=3,
                unique_id='3',
                phone_number='01055556666',
                name='김응남',
                gender=1,
                birth_year=1955,
                birth_date='0101',
                point=3000,
                reported_count=0,
                is_deleted=1,
            ),
            User(
                id=4,
                unique_id='4',
                phone_number='01077778888',
                name='곽철용',
                gender=1,
                birth_year=1965,
                birth_date='0101',
                point=3000,
                reported_count=0,
                is_deleted=1,
            ),
            User(
                id=5,
                unique_id='5',
                phone_number='01099991111',
                name='오미자',
                gender=2,
                birth_year=1960,
                birth_date='0101',
                point=3000,
                reported_count=0,
                is_deleted=1,
            ),
            User(
                id=6,
                unique_id='6',
                phone_number='01022223333',
                name='윤숙자',
                gender=2,
                birth_year=1963,
                birth_date='0101',
                point=3000,
                reported_count=0,
                is_deleted=1,
            ),
            User(
                id=7,
                unique_id='7',
                phone_number='01044445555',
                name='홍경자',
                gender=2,
                birth_year=1964,
                birth_date='0101',
                point=3000,
                reported_count=0,
                is_deleted=1,
            ),
            User(
                id=8,
                unique_id='8',
                phone_number='01066667777',
                name='최장미',
                gender=2,
                birth_year=1965,
                birth_date='0101',
                point=3000,
                reported_count=0,
                is_deleted=1,
            ),
            User(
                id=9,
                unique_id='9',
                phone_number='01088889999',
                name='김갑룡',
                gender=1,
                birth_year=1966,
                birth_date='0101',
                point=3000,
                reported_count=0,
                is_deleted=1,
            )
        ])

        Location.objects.bulk_create([
            Location(
                id=1,
                longtitude=127.123456,
                latitude=30.123456,
                max_distance=2000,
                user_id=1,
            ),
            Location(
                id=2,
                longtitude=124.123456,
                latitude=30.123456,
                max_distance=2,
                user_id=2,
            ),
            Location(
                id=3,
                longtitude=120.123456,
                latitude=35.123456,
                max_distance=10,
                user_id=3,
            ),
            Location(
                id=4,
                longtitude=122.123456,
                latitude=32.123456,
                max_distance=30,
                user_id=4,
            ),
            Location(
                id=5,
                longtitude=128.123456,
                latitude=35.123456,
                max_distance=5,
                user_id=5,
            ),
            Location(
                id=6,
                longtitude=120.123456,
                latitude=38.123456,
                max_distance=100,
                user_id=6,
            ),
        ])

        Wishlist.objects.create(
            id=1,
            user_id=1,
            liked_user_id=7
        )

    def tearDown(self):
        User.objects.all().delete()
        Location.objects.all().delete()
        Wishlist.objects.all().delete()

    def test_get_user_mylike_success(self):
        token = jwt.encode({'id': 1}, SECRET_KEY, ALGORITHM)
        client = Client()
        headers = {'HTTP_Authorization': token}
        response = client.get('/pairs/mylike', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['id'], 7)

    def test_success_location_get(self):
        token = jwt.encode({'id': 1}, SECRET_KEY, ALGORITHM)
        client = Client()
        headers = {'HTTP_Authorization': token}
        response = client.get('/pairs', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                         {
                             "longtitude": "127.123456",
                             "latitude": "30.123456",
                             "max_distance": 2000,
                             "user": 1
                         })

    def test_fail_location_get_invalid_user(self):
        token = jwt.encode({'id': 20}, SECRET_KEY, ALGORITHM)
        client = Client()
        headers = {'HTTP_Authorization': token}
        response = client.get('/pairs', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
                         {
                             "message": "INVALID_USER"
                         })

    def test_success_location_post_create(self):
        token = jwt.encode({'id': 7}, SECRET_KEY, ALGORITHM)
        client = Client()
        headers = {'HTTP_Authorization': token}
        location = {
            "longtitude": 128.993555,
            "latitude": 30.52106,
            "max_distance": 20,
            "user": 7
        }
        response = client.post('/pairs', json.dumps(location), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),
                         {
                             "message": "SUCCESS"
                         })

    def test_fail_location_post_create_exist_user(self):
        token = jwt.encode({'id': 1}, SECRET_KEY, ALGORITHM)
        client = Client()
        headers = {'HTTP_Authorization': token}
        location = {
            "longtitude": 128.993555,
            "latitude": 30.52106,
            "max_distance": 20,
            "user": 1
        }
        response = client.post('/pairs', json.dumps(location), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
                         {
                             'message': 'EXIST_USER'
                         })

    def test_fail_location_post_create_invalid_user(self):
        token = jwt.encode({'id': 40}, SECRET_KEY, ALGORITHM)
        client = Client()
        headers = {'HTTP_Authorization': token}
        location = {
            "longtitude": 128.993555,
            "latitude": 30.52106,
            "max_distance": 20,
            "user": 40
        }
        response = client.post('/pairs', json.dumps(location), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
                         {
                             'message': 'INVALID_USER'
                         })

    def test_fail_location_post_create_wrong_contents(self):
        token = jwt.encode({'id': 7}, SECRET_KEY, ALGORITHM)
        client = Client()
        headers = {'HTTP_Authorization': token}
        location = {
            "longtitude": 128.993555,
            "latitude": 30.52106,
            "max_distance": "ddddddd",
        }
        response = client.post('/pairs', json.dumps(location), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
                         {
                             'max_distance': ['A valid integer is required.']
                         })

    def test_success_location_patch_update(self):
        token = jwt.encode({'id': 6}, SECRET_KEY, ALGORITHM)
        client = Client()
        headers = {'HTTP_Authorization': token}
        location = {
            "longtitude": 128.993555,
            "latitude": 30.52106,
            "max_distance": 500,
            "user": 6
        }
        response = client.patch('/pairs', json.dumps(location), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                         {
                             'message': 'SUCCESS'
                         })

    def test_success_match_get_user_with_base_information(self):
        token = jwt.encode({'id': 1}, SECRET_KEY, ALGORITHM)
        client = Client()
        headers = {'HTTP_Authorization': token}
        response = client.get('/pairs/match', **headers)

        self.maxDiff = None
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
                         [
                             {
                                 "id": 5,
                                 "phone_number": "01099991111",
                                 "name": "오미자",
                                 "gender": 2,
                                 "birth_year": 1960,
                                 "location_set": [
                                     {
                                         "longtitude": "128.123456",
                                         "latitude": "35.123456",
                                         "max_distance": 5,
                                         "user": 5
                                     }
                                 ],
                                 "to_user_set": []
                             },
                             {
                                 "id": 6,
                                 "phone_number": "01022223333",
                                 "name": "윤숙자",
                                 "gender": 2,
                                 "birth_year": 1963,
                                 "location_set": [
                                     {
                                         "longtitude": "120.123456",
                                         "latitude": "38.123456",
                                         "max_distance": 100,
                                         "user": 6
                                     }
                                 ],
                                 "to_user_set": []
                             }
                         ]
                         )