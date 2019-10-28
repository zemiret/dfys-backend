import os

import pytest
from django.utils.dateparse import parse_datetime
from rest_framework import serializers
from rest_framework.test import APIRequestFactory

from dfys.core.models import Category, Skill, Activity, ActivityEntry
from dfys.core.serializers import CategoryFlatSerializer, SkillFlatSerializer, SkillDeepSerializer, \
    ActivityFlatSerializer, CategoryInSkillSerializer, ActivityDeepSerializer, SkillListSerializer
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
class TestSkillListSerializer:
    def test_serialization(self):
        skill = SkillFactory(name='TestSkill')
        categories = skill.categories.all()
        request = create_user_request(APIRequestFactory().post)

        s = SkillListSerializer({
            'skills': [skill],
            'categories': categories,
        })

        skills = s.data['skills']
        res_cat = s.data['categories']

        assert len(res_cat) == 2
        assert len(skills) == 1

        for i in (0, 1):
            cat_id = categories[i].id

            assert res_cat[cat_id]['id'] == categories[i].id
            assert res_cat[cat_id]['name'] == categories[i].name
            assert res_cat[cat_id]['is_base_category'] == categories[i].is_base_category

    def test_create(self):
        with pytest.raises(serializers.ValidationError):
            request = create_user_request(APIRequestFactory().post)
            fake_cat = CategoryFactory().id

            s = SkillListSerializer(data={
                'skills': [],
                'categories': [fake_cat]
            }, context={
                'request': request
            })

            s.is_valid(raise_exception=True)
            s.save()

    def test_update(self):
        with pytest.raises(serializers.ValidationError):
            request = create_user_request(APIRequestFactory().post)
            fake_cat = CategoryFactory().id

            s = SkillListSerializer(data={
                'skills': [],
                'categories': [fake_cat]
            }, context={
                'request': request
            }, instance={
                'skills': [],
                'categories': [],
            })

            s.is_valid(raise_exception=True)
            s.save()


@pytest.mark.django_db
class TestSkillDeepSerializer:
    def test_serialization(self, mocker):
        mocker.patch('django.utils.timezone.now', mock_now)

        skill = SkillFactory(name='TestSkill')
        categories = skill.categories.all()
        act = ActivityFactory(title='Act1', category=categories[0], skill=skill)

        s = SkillDeepSerializer(skill, context={'request': None})

        data = s.data
        data['add_date'] = parse_datetime(data['add_date'])
        data_act = data['activities'][act.id]
        data_act['add_date'] = parse_datetime(data_act['add_date'])
        data_act['modify_date'] = parse_datetime(data_act['modify_date'])

        assert data == dict(
            id=skill.id,
            name='TestSkill',
            add_date=mock_now(),
            categories={
                categories[0].id: dict(
                    id=categories[0].id,
                    name=categories[0].name,
                ),
                categories[1].id: dict(
                    id=categories[1].id,
                    name=categories[1].name,
                )
            },
            activities={
                act.id: dict(
                    id=act.id,
                    title=act.title,
                    category=categories[0].id,
                    skill=skill.id,
                    description=act.description,
                    add_date=mock_now(),
                    modify_date=mock_now()
                )
            }
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
        s = CategoryInSkillSerializer(cat)

        assert s.data['name'] == cat.name


@pytest.mark.django_db
class TestActivityDeepSerializer:
    def test_serialization(self, mocker):
        mocker.patch('django.utils.timezone.now', mock_now)
        act = ActivityFactory()
        attachment = AttachmentFactory(activity=act)
        comment = CommentFactory(activity=act)

        s = ActivityDeepSerializer(act)

        data = s.data

        comment_data = data['entries'][comment.id]
        attachment_data = data['entries'][attachment.id]

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
            entries={
                attachment.id: dict(
                    id=attachment.id,
                    add_date=mock_now(),
                    modify_date=mock_now(),
                    comment=''
                ),
                comment.id: dict(
                    id=comment.id,
                    add_date=mock_now(),
                    modify_date=mock_now(),
                    comment=comment.comment,
                ),
            }
        )
