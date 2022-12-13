from django.contrib.auth.models import User
from ecommerce.models import Item, Order
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status


class EcommerceTestCase(APITestCase):
    """ Test for Items and Orders """

    def setUp(self):
        # creating test item objects
        Item.objects.create(title='Demo item 1', description='Desc for demo 1', price=500, stock=20)
        Item.objects.create(title='Demo item 2', description='Desc for demo 2', price=200, stock=15)
        Item.objects.create(title='Demo item 3', description='Desc for demo 3', price=300, stock=10)
        Item.objects.create(title='Demo item 4', description='Desc for demo 4', price=900, stock=5)
        Item.objects.create(title='Demo item 5', description='Desc for demo 5', price=100, stock=30)
        # getting all item objects
        self.items = Item.objects.all()
        # creating test user object
        self.user = User.objects.create_user(username='testuser1', password='this_is_a_test', email='test@test.com')
        # creating an order object with a test item and a test user
        Order.objects.create(item=Item.objects.first(), user=User.objects.first(), quantity=1)
        Order.objects.create(item=Item.objects.first(), user=User.objects.first(), quantity=2)

        # the app uses token authentication
        self.token = Token.objects.get(user=self.user)
        self.client = APIClient()

        # we pass the token in all calls to the API
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_all_items(self):
        """ test ItemsViewSet list method"""
        self.assertEqual(self.items.count(), 5)
        response = self.client.get('/item/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_one_item(self):
        """ test ItemsViewSet retrieve method"""
        for item in self.items:
            response = self.client.get(f'/item/{item.id}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_is_more_than_stock(self):
        """ test Item.check_stock when order.quantity > item.stock """
        for item in self.items:
            current_stock = item.stock
            self.assertEqual(item.check_stock(current_stock + 1), False)

    def test_order_equals_stock(self):
        """ test Item.check_stock when order.quantity == item.stock """
        for item in self.items:
            current_stock = item.stock
            self.assertEqual(item.check_stock(current_stock), True)

    def test_order_is_less_than_Stock(self):
        """ test Item.check_stock when order.quantity < item.stock """
        for item in self.items:
            current_stock = item.stock
            self.assertTrue(item.check_stock(current_stock - 1), True)

    def test_create_order_with_more_than_stock(self):
        """ test OrdersViewSet create method when order.quantity > item.stock """
        for item in self.items:
            stock = item.stock
            data = {'item': str(item.id), 'quantity': str(stock+1)}
            response = self.client.post(f'/order/', data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_less_than_stock(self):
        """ test OrdersViewSet create method when order.quantity < item.stock """
        for item in self.items:
            data = {'item': str(item.id), 'quantity': 1}
            response = self.client.post(f'/order/', data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_order_with_equal_stock(self):
        """ test OrdersViewSet create method when order.quantity == item.stock """
        for item in self.items:
            stock = item.stock
            data = {'item': str(item.id), 'quantity': str(stock)}
            response = self.client.post(f'/order/', data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_orders(self):
        """ test OrdersViewSet list method """
        self.assertEqual(Order.objects.count(), 2)
        response = self.client.get('/order/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_one_order(self):
        """ test OrdersViewSet retrieve method """
        orders = Order.objects.filter(user=self.user)
        for order in orders:
            response = self.client.get(f'/order/{order.id}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
