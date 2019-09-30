
import pytest
from django.utils.dateparse import parse_datetime
from rest_framework.test import APIRequestFactory

from dfys.core.models import Category, Skill
from dfys.core.serializers import CategorySerializer, FlatSkillSerializer
from dfys.core.tests.test_factory import CategoryFactory, UserFactory, SkillFactory
from dfys.core.tests.utils import create_user_request, mock_timezone_now


@pytest.mark.django_db
class TestCategorySerializer:
    def test_serialization(self):
        category = CategoryFactory(is_base_category=False)
        s = CategorySerializer(category)

        assert s.data == dict(id=category.id,
                              name=category.name,
                              is_base_category=False)

    def test_create(self):
        request = create_user_request(APIRequestFactory().post)
        category_name = 'CatName'
        is_base = True

        s = CategorySerializer(data={
            'name': category_name,
            'is_base_category': is_base
        }, context={
            'request': request
        })
        s.is_valid(raise_exception=True)
        cat = Category.objects.get(id=s.save().id)

        assert cat.name == category_name
        assert cat.is_base_category is is_base

    def test_update(self):
        cat = CategoryFactory(is_base_category=False)
        request = create_user_request(APIRequestFactory().put)

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


@pytest.mark.django_db
class TestFlatSkillSerializer:
    @mock_timezone_now
    def test_serialization(self, testtime=None):
        skill = SkillFactory(name='Testname')
        s = FlatSkillSerializer(skill)

        assert len(s.data['categories']) == 2
        assert s.data['name'] == 'Testname'
        assert parse_datetime(s.data['add_date']) == testtime

    @mock_timezone_now
    def test_create(self, testtime=None):
        request = create_user_request(APIRequestFactory().post)
        required_category = CategoryFactory(is_base_category=True,
                                            owner=request.user)

        s = FlatSkillSerializer(data={
            'name': 'TestSkill'
        }, context={
            'request': request
        })

        s.is_valid(raise_exception=True)
        skill = Skill.objects.get(id=s.save().id)

        assert len(skill.categories.get_queryset()) == 1
        assert skill.name == 'TestSkill'
        assert skill.add_date == testtime
        assert skill.owner == request.user

    def test_update(self):
        request = create_user_request(APIRequestFactory().put)
        skill = SkillFactory(name='OldName')

        s = FlatSkillSerializer(instance=skill, data={
            'name': 'NewName'
        }, context={
            'request': request
        })

        s.is_valid(raise_exception=True)
        skill = Skill.objects.get(id=s.save().id)

        assert skill.name == 'NewName'
        assert skill.owner == request.user
