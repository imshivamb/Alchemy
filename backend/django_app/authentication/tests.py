from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, UserProfile

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_login(self):
        # Create user first
        User.objects.create_user(
            email='test@example.com',
            password='StrongPass123!'
        )
        
        # Try logging in
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_password_reset(self):
        # Create user
        user = User.objects.create_user(
            email='test@example.com',
            password='StrongPass123!'
        )

        # Request password reset
        response = self.client.post(reverse('password-reset'), {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserLimitsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_user_limits(self):
        response = self.client.get(reverse('user-limits'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('limits', response.data)
        self.assertIn('workflows', response.data['limits'])
        self.assertIn('api_keys', response.data['limits'])