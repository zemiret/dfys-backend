from django.urls import reverse
from rest_framework.test import APITestCase

from dfys.core.tests.test_factory import CategoryFactory


class TestCategoryViewSet(APITestCase):
    def test_creating(self):
        pass

    def test_list(self):
        cat1 = CategoryFactory(is_base_category=True)
        cat2 = CategoryFactory(is_base_category=True)
        cat3 = CategoryFactory(is_base_category=False)

        self.client.force_login(cat1.owner)
        # TODO: Fix this test, write the rest
        self.assertEqual(self.client.get(reverse('category-list')).data, [cat3, cat2, cat1])

    def test_deletion(self):
        pass

    def test_deletion_of_base_category(self):
        """
        Deletion of base category should not be possible
        """
        pass
