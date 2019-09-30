from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from dfys.core.models import Category
from dfys.core.serializers import CategorySerializer
from dfys.core.tests.test_factory import CategoryFactory, UserFactory


class TestCategoryViewSet(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_create(self):
        cat_name = 'CatName'
        is_base = True

        self.client.force_login(self.user)
        response = self.client.post(reverse('category-list'), data={
            'name': cat_name,
            'is_base_category': is_base
        })

        created_cat = Category.objects.get(id=response.data['id'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(created_cat.name, cat_name)
        self.assertEqual(created_cat.is_base_category, is_base)
        self.assertEqual(created_cat.owner.id, self.user.id)

    def test_invalid_create(self):
        cat_name = ''
        is_base = True

        self.client.force_login(self.user)
        response = self.client.post(reverse('category-list'), data={
            'name': cat_name,
            'is_base_category': is_base
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list(self):
        cat1 = CategoryFactory(is_base_category=True)
        cat2 = CategoryFactory(is_base_category=True)
        cat3 = CategoryFactory(is_base_category=False)
        s = CategorySerializer([cat3, cat2, cat1], many=True)

        self.client.force_login(cat1.owner)
        response = self.client.get(reverse('category-list'))

        self.assertEqual(response.data, s.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy(self):
        cat = CategoryFactory(is_base_category=False)

        self.client.force_login(self.user)
        response = self.client.delete(reverse('category-detail', kwargs={'pk': cat.id}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.filter(id=cat.id).exists(), False)

    def test_destroy_of_base_category(self):
        """
        Deletion of base category should not be possible
        """
        cat = CategoryFactory(is_base_category=True)

        self.client.force_login(self.user)
        response = self.client.delete(reverse('category-detail', kwargs={'pk': cat.id}))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.filter(id=cat.id).exists(), True)


class TestSkillViewSet(APITestCase):
    def test_create(self):
        pass

    def test_list(self):
        """
        Should provide skills flatter overview
        """
        pass

    def test_details(self):
        """
        Should provide skill detailed deep overview
        """
        pass

    def test_destroy(self):
        pass
