import os

import pytest
from django.utils.dateparse import parse_datetime
from rest_framework import serializers
from rest_framework.test import APIRequestFactory

from dfys.core.models import Category, Skill, Activity, ActivityEntry
from dfys.core.serializers import CategoryFlatSerializer, SkillFlatSerializer, SkillDeepSerializer, \
    ActivityFlatSerializer, CategoryInSkillSerializer, ActivityDeepSerializer
from dfys.core.tests.test_factory import CategoryFactory, SkillFactory, ActivityFactory, CommentFactory, \
    AttachmentFactory
from dfys.core.tests.utils import create_user_request, mock_now


@pytest.mark.django_db
class TestCategoryFlatSerializer:
    def test_serialization(self):
        category = CategoryFactory(is_base_category=False)
        s = CategoryFlatSerializer(category)

        assert s.data == dict(id=category.id,
                              name=category.name,
                              is_base_category=False)

    def test_create(self):
        request = create_user_request(APIRequestFactory().post)
        category_name = 'CatName'

        s = CategoryFlatSerializer(data={
            'name': category_name,
        }, context={
            'request': request
        })
        s.is_valid(raise_exception=True)
        cat = Category.objects.get(id=s.save().id)

        assert cat.name == category_name

    def test_update(self):
        cat = CategoryFactory(is_base_category=False)
        request = create_user_request(APIRequestFactory().put)

        s = CategoryFlatSerializer(instance=cat, data={
            'name': 'NewName',
        }, context={
            'request': request
        })

        s.is_valid(raise_exception=True)
        cat = Category.objects.get(id=s.save().id)

        assert cat.name == 'NewName'


@pytest.mark.django_db
class TestSkillFlatSerializer:
    def test_serialization(self, mocker):
        mocker.patch('django.utils.timezone.now', mock_now)
        skill = SkillFactory(name='Testname')
        s = SkillFlatSerializer(skill)

        assert len(s.data['categories']) == 2
        assert s.data['name'] == 'Testname'
        assert parse_datetime(s.data['add_date']) == mock_now()

    def test_create(self, mocker):
        mocker.patch('django.utils.timezone.now', mock_now)
        request = create_user_request(APIRequestFactory().post)
        _required_category = CategoryFactory(is_base_category=True,
                                             owner=request.user)

        s = SkillFlatSerializer(data={
            'name': 'TestSkill'
        }, context={
            'request': request
        })

        s.is_valid(raise_exception=True)
        skill = Skill.objects.get(id=s.save().id)

        assert len(skill.categories.get_queryset()) == 1
        assert skill.name == 'TestSkill'
        assert skill.add_date == mock_now()
        assert skill.owner == request.user

    def test_update(self):
        request = create_user_request(APIRequestFactory().put)
        skill = SkillFactory(name='OldName')

        s = SkillFlatSerializer(instance=skill, data={
            'name': 'NewName'
        }, context={
            'request': request
        })

        s.is_valid(raise_exception=True)
        skill = Skill.objects.get(id=s.save().id)

        assert skill.name == 'NewName'
        assert skill.owner == request.user


@pytest.mark.django_db
class TestSkillDeepSerializer:
    def test_serialization(self, mocker):
        mocker.patch('django.utils.timezone.now', mock_now)

        skill = SkillFactory(name='TestSkill')
        categories = skill.categories.all()
        act = ActivityFactory(title='Act1', category=categories[0], skill=skill)

        s = SkillDeepSerializer(skill)

        data = s.data
        data['add_date'] = parse_datetime(data['add_date'])
        data_act = data['categories'][0]['activities'][0]
        data_act['add_date'] = parse_datetime(data_act['add_date'])
        data_act['modify_date'] = parse_datetime(data_act['modify_date'])

        assert data == dict(
            id=skill.id,
            name='TestSkill',
            add_date=mock_now(),
            categories=[
                dict(
                    id=categories[0].id,
                    name=categories[0].name,
                    activities=[
                        dict(
                            id=act.id,
                            title=act.title,
                            category=categories[0].id,
                            skill=skill.id,
                            description=act.description,
                            add_date=mock_now(),
                            modify_date=mock_now()
                        )
                    ]
                ),
                dict(
                    id=categories[1].id,
                    name=categories[1].name,
                    activities=[]
                )
            ]
        )

    def test_create(self):
        with pytest.raises(serializers.ValidationError):
            request = create_user_request(APIRequestFactory().post)
            fake_cat = CategoryFactory()

            s = SkillDeepSerializer(data={
                'name': 'SkillName',
                'categories': [fake_cat.id]
            }, context={
                'request': request
            })

            s.is_valid(raise_exception=True)
            s.save()

    def test_update(self):
        with pytest.raises(serializers.ValidationError):
            request = create_user_request(APIRequestFactory().post)
            skill = SkillFactory(name='OldName')
            fake_cat = CategoryFactory()

            s = SkillDeepSerializer(instance=skill, data={
                'name': 'NewName',
                'categories': [fake_cat.id]
            }, context={
                'request': request
            })

            s.is_valid()
            s.save()


@pytest.mark.django_db
class TestActivityFlatSerializer:
    def test_serialization(self):
        act = ActivityFactory()
        s = ActivityFlatSerializer(act)

        assert s.data['id'] == act.id
        assert s.data['title'] == act.title
        assert s.data['skill'] == act.skill.id
        assert s.data['category'] == act.category.id
        assert s.data['description'] == act.description

    def test_create(self, mocker):
        mocker.patch('django.utils.timezone.now', mock_now)
        request = create_user_request(APIRequestFactory().post)
        skill = SkillFactory()
        categories = skill.categories.all()

        s = ActivityFlatSerializer(data=dict(
            title='NewAct',
            skill=skill.id,
            category=categories[0].id,
            description='desc',
        ), context={
            'request': request
        })

        s.is_valid(raise_exception=True)
        act = Activity.objects.get(id=s.save().id)

        assert act.title == 'NewAct'
        assert act.skill.id == skill.id
        assert act.category.id == categories[0].id
        assert act.description == 'desc'

    def test_update(self, mocker):
        mocker.patch('django.utils.timezone.now', mock_now)
        request = create_user_request(APIRequestFactory().post)
        skill = SkillFactory()
        categories = skill.categories.all()
        act = ActivityFactory(skill=skill, category=categories[0])

        s = ActivityFlatSerializer(instance=act, data=dict(
            title='ModifiedAct',
            skill=skill.id,
            category=categories[1].id,
            description='new_desc',
        ), context={
            'request': request
        })

        s.is_valid(raise_exception=True)
        act = Activity.objects.get(id=s.save().id)

        assert act.title == 'ModifiedAct'
        assert act.skill.id == skill.id
        assert act.category.id == categories[1].id
        assert act.description == 'new_desc'


@pytest.mark.django_db
class TestCategoryInSkillSerializer:
    def test_serialization(self, mocker):
        mocker.patch('django.utils.timezone.now', mock_now)
        cat = CategoryFactory()
        act = ActivityFactory(category=cat)
        s = CategoryInSkillSerializer(cat)

        print(s.data)

        activity = s.data['activities'][0]

        assert s.data['name'] == cat.name
        assert activity['title'] == act.title
        assert activity['category'] == cat.id
        assert activity['skill'] == act.skill.id
        assert activity['description'] == act.description
        assert parse_datetime(activity['add_date']) == mock_now()
        assert parse_datetime(activity['modify_date']) == mock_now()


@pytest.mark.django_db
class TestActivityDeepSerializer:
    def test_serialization(self, mocker):
        mocker.patch('django.utils.timezone.now', mock_now)
        act = ActivityFactory()
        attachment = AttachmentFactory(activity=act)
        comment = CommentFactory(activity=act)

        s = ActivityDeepSerializer(act)

        data = s.data

        from pprint import pprint
        pprint(data)

        comment_data = data['entries'][0]
        attachment_data = data['entries'][1]

        data['add_date'] = parse_datetime(data['add_date'])
        data['modify_date'] = parse_datetime(data['modify_date'])
        comment_data['add_date'] = parse_datetime(comment_data['add_date'])
        comment_data['modify_date'] = parse_datetime(comment_data['modify_date'])
        attachment_data['add_date'] = parse_datetime(attachment_data['add_date'])
        attachment_data['modify_date'] = parse_datetime(attachment_data['modify_date'])

        assert data == dict(
            id=act.id,
            title=act.title,
            description=act.description,
            skill=act.skill.id,
            category=act.category.id,
            add_date=mock_now(),
            modify_date=mock_now(),
            entries=[
                dict(
                    id=comment.id,
                    type=ActivityEntry.COMMENT,
                    add_date=mock_now(),
                    modify_date=mock_now(),
                    comment_content=comment.comment_content,
                    attachment_content=None
                ),
                dict(
                    id=attachment.id,
                    type=ActivityEntry.ATTACHMENT,
                    add_date=mock_now(),
                    modify_date=mock_now(),
                    attachment_content=None,
                    comment_content=None
                )
            ]
        )
