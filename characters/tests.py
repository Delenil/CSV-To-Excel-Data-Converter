from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Character
from io import StringIO

class CharacterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='password123')

    def setUp(self):
        self.client.login(username='testuser', password='password123')

    def test_character_creation_valid(self):
        response = self.client.post(reverse('add_character'), {
            'name': 'Gandalf',
            'class': 'Mage',
            'position': 'Ranged_Dps'
        })
        self.assertRedirects(response, reverse('character_list'))
        self.assertTrue(Character.objects.filter(name='Gandalf').exists())

    def test_character_creation_invalid_name(self):
        response = self.client.post(reverse('add_character'), {
            'name': 'gandalf',  # Invalid because it doesn't start with a capital letter
            'class': 'Mage',
            'position': 'Ranged_Dps'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Name must start with a capital letter.')

    def test_character_creation_invalid_class_position(self):
        response = self.client.post(reverse('add_character'), {
            'name': 'Gandalf',
            'class': 'Paladin',  # Invalid class for Ranged_Dps
            'position': 'Ranged_Dps'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Paladin cannot be a Ranged_Dps.')

    def test_character_creation_tank_limit(self):
        Character.objects.create(name='Tank1', character_class='Paladin', position='Tank', user=self.user)
        Character.objects.create(name='Tank2', character_class='Warrior', position='Tank', user=self.user)

        response = self.client.post(reverse('add_character'), {
            'name': 'Tank3',
            'class': 'Paladin',
            'position': 'Tank'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There cannot be more than 2 Tanks.')

    def test_duplicate_character_names(self):
        Character.objects.create(name='Gandalf', character_class='Mage', position='Ranged_Dps', user=self.user)

        response = self.client.post(reverse('add_character'), {
            'name': 'Gandalf',
            'class': 'Warlock',
            'position': 'Ranged_Dps'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Names cannot be the same for the same user.')

    def test_character_list_view(self):
        Character.objects.create(name='Gandalf', character_class='Mage', position='Ranged_Dps', user=self.user)
        response = self.client.get(reverse('character_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'character_list.html')
        self.assertContains(response, 'Gandalf')

    def test_character_delete(self):
        character = Character.objects.create(name='Gandalf', character_class='Mage', position='Ranged_Dps', user=self.user)
        response = self.client.post(reverse('delete_character', args=[character.id]))
        self.assertRedirects(response, reverse('character_list'))
        self.assertFalse(Character.objects.filter(id=character.id).exists())

    def test_csv_upload_valid(self):
        csv_content = "Name: Gandalf\nClass: Mage\nPosition: Ranged_Dps\n\n"
        # Use StringIO to simulate a file-like object
        csv_file = StringIO(csv_content)
        csv_file.name = 'test.csv'  # Set a name to simulate a real file
        response = self.client.post(reverse('upload_csv'), {'file': csv_file})
        self.assertRedirects(response, reverse('character_list'))
        self.assertTrue(Character.objects.filter(name='Gandalf').exists())

    def test_csv_upload_invalid(self):
        csv_content = "Name: gandalf\nClass: Paladin\nPosition: Ranged_Dps\n\n"
        # Use StringIO to simulate a file-like object
        csv_file = StringIO(csv_content)
        csv_file.name = 'test.csv'  # Set a name to simulate a real file
        response = self.client.post(reverse('upload_csv'), {'file': csv_file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Name must start with a capital letter.')

    def test_export_to_excel(self):
        Character.objects.create(name='Gandalf', character_class='Mage', position='Ranged_Dps', user=self.user)
        response = self.client.get(reverse('export_to_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=characters.xlsx')

    def test_delete_character(self):
        character = Character.objects.create(name='Gandalf', character_class='Mage', position='Ranged_Dps',
                                             user=self.user)
        response = self.client.post(reverse('delete_character', args=[character.id]))
        self.assertRedirects(response, reverse('character_list'))
        self.assertFalse(Character.objects.filter(id=character.id).exists())

    def test_delete_character_not_found(self):
        response = self.client.post(reverse('delete_character', args=[999]))  # Non-existent character ID
        self.assertEqual(response.status_code, 404)


    def test_export_to_excel_no_characters(self):
        response = self.client.get(reverse('export_to_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No characters available to export.')

    def test_register_user_valid(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'Password123!',
            'password2': 'Password123!'
        })
        self.assertRedirects(response, reverse('character_list'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_user_invalid(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'Password123!',
            'password2': 'differentpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The two password fields didn’t match.')

    def test_login_user_valid(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('character_list'))

    def test_login_user_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid credentials')

    def test_logout_user(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('landing_page'))
        # Check that the user is logged out
        response = self.client.get(reverse('character_list'))
        self.assertRedirects(response, reverse('login'))