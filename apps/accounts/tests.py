from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user_with_default_role(self):
        user = User.objects.create_user(
            username='operateur1',
            password='Test12345'
        )
        self.assertEqual(user.role, User.Role.OPERATOR)
        self.assertFalse(user.is_banned)

    def test_ban_user(self):
        user = User.objects.create_user(
            username='user_ban',
            password='Test12345'
        )
        user.ban()
        user.refresh_from_db()
        self.assertTrue(user.is_banned)

    def test_reactivate_user(self):
        user = User.objects.create_user(
            username='user_reactivate',
            password='Test12345',
            is_banned=True
        )
        user.reactivate()
        user.refresh_from_db()
        self.assertFalse(user.is_banned)


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='operateur_login',
            password='Test12345',
            role=User.Role.OPERATOR
        )

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'operateur_login',
            'password': 'Test12345',
        })
        self.assertEqual(response.status_code, 302)

    def test_banned_user_cannot_login(self):
        self.user.is_banned = True
        self.user.save()

        response = self.client.post(reverse('login'), {
            'username': 'operateur_login',
            'password': 'Test12345',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Votre compte a été banni")


class UserManagementPermissionsTests(TestCase):
    def setUp(self):
        self.superadmin = User.objects.create_user(
            username='superadmin',
            password='Test12345',
            role=User.Role.SUPERADMIN
        )
        self.admin = User.objects.create_user(
            username='admin1',
            password='Test12345',
            role=User.Role.ADMIN
        )
        self.operator = User.objects.create_user(
            username='operator1',
            password='Test12345',
            role=User.Role.OPERATOR
        )

    def test_operator_cannot_access_user_list(self):
        self.client.login(username='operator1', password='Test12345')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 302)

    def test_admin_can_access_user_list(self):
        self.client.login(username='admin1', password='Test12345')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)

    def test_admin_does_not_see_superadmin_in_user_list(self):
        self.client.login(username='admin1', password='Test12345')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'superadmin')

    def test_superadmin_sees_all_users(self):
        self.client.login(username='superadmin', password='Test12345')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admin1')
        self.assertContains(response, 'operator1')

    def test_admin_cannot_update_superadmin(self):
        self.client.login(username='admin1', password='Test12345')
        response = self.client.get(reverse('user_update', args=[self.superadmin.pk]))
        self.assertEqual(response.status_code, 302)

    def test_user_cannot_delete_self(self):
        self.client.login(username='admin1', password='Test12345')
        response = self.client.post(reverse('user_delete', args=[self.admin.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())