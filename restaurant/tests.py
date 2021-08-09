from restaurant.models import Reservation, Table
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient

User = get_user_model()

class TestUsers(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(employee_number=1000, username='admin_user', password="test_pass")
        self.url = "/api/user/create_employee/"
        self.client = APIClient()
        self.client.force_login(self.admin_user)

    def test_success_create_employee(self):
        data = {
            "employee_number": 2000,
            "username": "Test Employee 1",
            "password": "test_employee"
        }
        resp = self.client.post(self.url, data=data)
        
        self.assertEqual(resp.status_code, 201)

    def test_duplicate_employee_number(self):
        data1 = {
            "employee_number": 2000,
            "username": "Test Employee 1",
            "password": "test_employee"
        }
        self.client.post(self.url, data=data1)
        
        data2 = {
            "employee_number": 2000,
            "username": "Test Employee 2",
            "password": "test_employee"
        }
        resp = self.client.post(self.url, data=data2)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['employee_number'][0], 'user with this employee number already exists.')

    def test_invalid_password(self):
        data = {
            "employee_number": 2000,
            "username": "Test Employee 1",
            "password": "test"
        }
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['password'][0], 'This password is too short. It must contain at least 6 characters.')


class TestRestaurantAPIs(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(employee_number=1000, username='admin_user', password="test_pass")
        self.employee_user = User.objects.create_user(employee_number=2000, username="employee_user", password="test_pass")
        
        self.tables_url = '/api/restaurant/tables/'
        self.reservation_url = "/api/restaurant/reservation/"

        self.table_1 = Table.objects.create(**{"table_number": 1, "table_number_of_seats": 4})
        self.table_2 = Table.objects.create(**{"table_number": 2, "table_number_of_seats": 2})
        self.table_3 = Table.objects.create(**{"table_number": 5, "table_number_of_seats": 6})
        self.table_4 = Table.objects.create(**{"table_number": 7, "table_number_of_seats": 8})
        self.table_5 = Table.objects.create(**{"table_number": 15, "table_number_of_seats": 4})
        self.table_6 = Table.objects.create(**{"table_number": 20, "table_number_of_seats": 6})
        self.table_7 = Table.objects.create(**{"table_number": 11, "table_number_of_seats": 4})

        self.client = APIClient()
    
    # Tables Tests

    def test_add_table_success(self):
        self.client.force_login(self.admin_user)
        resp = self.client.post(self.tables_url, data={"table_number": 10, "table_number_of_seats": 4})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Table.objects.count(), 8)

    def test_employee_permission_denied_to_add_table(self):
        self.client.force_login(self.employee_user)
        resp = self.client.post(self.tables_url, data={"table_number": 30, "table_number_of_seats": 4})
        self.assertEqual(resp.status_code, 403)

    def test_duplicate_table_number(self):
        self.client.force_login(self.admin_user)
        resp = self.client.post(self.tables_url, data={"table_number": 1, "table_number_of_seats": 4})
        self.assertEqual(resp.status_code, 400)

    def test_delete_table_success(self):
        self.client.force_login(self.admin_user)
        resp = self.client.delete(f"{self.tables_url}11/")
        self.assertEqual(resp.status_code, 204)

    def test_delete_reserved_table(self):
        Reservation.objects.create(table=Table.objects.first(), reserve_start_time="13:30", reserve_end_time="14:00")
        self.client.force_login(self.admin_user)
        resp = self.client.delete(f"{self.tables_url}1/")
        self.assertEqual(resp.status_code, 403)

    
    # Reservation Tests

    def test_get_available_slots_with_minimum_table_seats(self):
        self.client.force_login(self.employee_user)
        resp = self.client.get(f"{self.reservation_url}check_available_time_slots/?required_seats=3")
        self.assertEqual(resp.status_code, 200)
        
        # should return 3 tables with the number of seats 4 which are (1, 11, 15)
        self.assertEqual(len(resp.json()), 3)
        self.assertEqual(list(resp.json().keys()), ['1','11','15'])