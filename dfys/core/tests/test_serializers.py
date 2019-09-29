import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from dfys.core.models import Category
from dfys.core.serializers import CategorySerializer
from dfys.core.tests.test_factory import CategoryFactory, UserFactory


@pytest.mark.django_db
class TestCategorySerializer:
    def test_serialization(self):
        category = CategoryFactory(is_base_category=False)
        s = CategorySerializer(category)

        assert s.data == dict(id=category.id,
                              name=category.name,
                              is_base_category=False)

    def test_update(self):
        cat = CategoryFactory(is_base_category=False)
        user = UserFactory()
        request = APIRequestFactory().put('/testpath')
        request.user = user

        s = CategorySerializer(instance=cat, data={
            'name': 'NewName',
            'is_base_category': True
        }, context={
            'request': request
        })

        s.is_valid(raise_exception=True)
        cat = Category.objects.get(id=s.save().id)

        assert cat.name == 'NewName'
        assert cat.is_base_category is True
