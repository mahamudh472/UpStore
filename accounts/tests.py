from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UserProfile
import datetime

class ProfileViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile, created = UserProfile.objects.get_or_create(user=self.user)
        
    def test_profile_view_requires_login(self):
        """Test that profile view requires authentication"""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_profile_view_authenticated_user(self):
        """Test profile view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile')
        
    def test_profile_update_valid_data(self):
        """Test profile update with valid data"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone_number': '1234567890',
            'gender': 'M',
            'date_of_birth': '1990-01-01',
            'bio': 'Test bio',
            'address': 'Test address'
        }
        
        response = self.client.post(reverse('accounts:profile'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Check if user data was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'john.doe@example.com')
        
        # Check if profile data was updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.phone_number, '1234567890')
        self.assertEqual(self.profile.gender, 'M')
        self.assertEqual(str(self.profile.date_of_birth), '1990-01-01')
        
    def test_profile_update_empty_date_of_birth(self):
        """Test profile update with empty date of birth"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone_number': '1234567890',
            'gender': 'M',
            'date_of_birth': '',  # Empty date
            'bio': 'Test bio',
            'address': 'Test address'
        }
        
        response = self.client.post(reverse('accounts:profile'), data)
        self.assertEqual(response.status_code, 302)  # Should succeed
        
        # Check if profile was updated (date should be None)
        self.profile.refresh_from_db()
        self.assertIsNone(self.profile.date_of_birth)
        
    def test_profile_update_invalid_email(self):
        """Test profile update with invalid email"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'invalid-email',  # Invalid email
            'phone_number': '1234567890',
            'gender': 'M',
            'date_of_birth': '1990-01-01',
            'bio': 'Test bio',
            'address': 'Test address'
        }
        
        response = self.client.post(reverse('accounts:profile'), data)
        # Since Django model validation will catch this, it should still redirect
        # but the email won't be updated
        self.assertEqual(response.status_code, 302)  # Redirect after processing
        
        # Check that email wasn't updated to invalid value
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'test@example.com')  # Original email unchanged
        
    def test_profile_update_future_date_of_birth(self):
        """Test profile update with future date of birth"""
        self.client.login(username='testuser', password='testpass123')
        
        future_date = datetime.date.today() + datetime.timedelta(days=1)
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone_number': '1234567890',
            'gender': 'M',
            'date_of_birth': future_date.strftime('%Y-%m-%d'),
            'bio': 'Test bio',
            'address': 'Test address'
        }
        
        response = self.client.post(reverse('accounts:profile'), data)
        self.assertEqual(response.status_code, 302)  # Redirect with error message
        
        # Check that date of birth wasn't updated to future date
        self.profile.refresh_from_db()
        self.assertNotEqual(str(self.profile.date_of_birth), future_date.strftime('%Y-%m-%d'))
        
    def test_profile_update_duplicate_email(self):
        """Test profile update with email that belongs to another user"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'other@example.com',  # Email belongs to another user
            'phone_number': '1234567890',
            'gender': 'M',
            'date_of_birth': '1990-01-01',
            'bio': 'Test bio',
            'address': 'Test address'
        }
        
        response = self.client.post(reverse('accounts:profile'), data)
        self.assertEqual(response.status_code, 302)  # Redirect with error message
        
        # Check that email wasn't changed to duplicate
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'test@example.com')  # Original email unchanged
