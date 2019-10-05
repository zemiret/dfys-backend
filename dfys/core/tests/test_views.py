from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from dfys.core.models import Category, Skill, ActivityEntry, Activity
from dfys.core.serializers import CategoryFlatSerializer
from dfys.core.tests.test_factory import CategoryFactory, UserFactory, SkillFactory, ActivityFactory, CommentFactory, \
    AttachmentFactory
from dfys.core.views import ActivitiesViewSet


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
        s = CategoryFlatSerializer([cat3, cat2, cat1], many=True)

        self.client.force_login(cat1.owner)
        response = self.client.get(reverse('category-list'))

        self.assertEqual(response.data, s.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy(self):
        cat = CategoryFactory(is_base_category=False)

        self.client.force_login(self.user)
        response = self.client.delete(reverse('category-detail', kwargs={'pk': cat.id}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=cat.id).exists())

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
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_create(self):
        skill_name = 'SkillName'
        self.client.force_login(self.user)
        response = self.client.post(reverse('skill-list'), data={
            'name': skill_name
        })

        skill = Skill.objects.get(id=response.data['id'])

        self.assertEqual(skill.name, skill_name)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list(self):
        """
        Should provide skills flatter overview
        """
        skill1 = SkillFactory(name='Skill1')
        skill2 = SkillFactory(name='Skill2')

        self.client.force_login(self.user)
        response = self.client.get(reverse('skill-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_details(self):
        """
        Should provide skill detailed deep overview
        """
        skill1 = SkillFactory(name='Skill1')
        skill2 = SkillFactory(name='Skill2')
        act1 = ActivityFactory(skill=skill1)
        act2 = ActivityFactory(skill=skill1)

        self.client.force_login(self.user)
        response = self.client.get(reverse('skill-detail', kwargs={'pk': skill1.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['categories']), 2)
        self.assertIn('activities', response.data['categories'][0])
        self.assertIn('activities', response.data['categories'][1])

    def test_destroy(self):
        skill1 = SkillFactory(name='Skill1')
        self.client.force_login(self.user)
        response = self.client.delete(reverse('skill-detail', kwargs={'pk': skill1.id}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Skill.objects.filter(id=skill1.id).exists())


class TestActivityViewSet(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_recent(self):
        act1 = ActivityFactory()
        act2 = ActivityFactory()
        act3 = ActivityFactory()

        self.client.force_login(self.user)
        response = self.client.get(reverse('activity-recent'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data[0]['id'], act3.id)
        self.assertEqual(response.data[1]['id'], act2.id)
        self.assertEqual(response.data[2]['id'], act1.id)

    def test_details(self):
        act = ActivityFactory()
        comment = CommentFactory(activity=act)
        attachment = AttachmentFactory(activity=act)

        self.client.force_login(self.user)
        response = self.client.get(reverse('activity-detail', kwargs={'pk': act.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['entries']), 2)
        self.assertEqual(response.data['entries'][0]['type'], ActivityEntry.ATTACHMENT)
        self.assertEqual(response.data['entries'][1]['type'], ActivityEntry.COMMENT)

    def test_create(self):
        skill = SkillFactory()
        cat = skill.categories.all()[0]

        self.client.force_login(self.user)

        response = self.client.post(reverse('activity-list'), data={
            'title': 'title',
            'category': cat.id,
            'skill': skill.id,
            'description': 'desc',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        activity = Activity.objects.get(id=response.data['id'])
        self.assertEqual(activity.title, 'title')
        self.assertEqual(activity.description, 'desc')
        self.assertEqual(activity.category, cat)
        self.assertEqual(activity.skill, skill)

    def test_adding_entry(self):
        raise Exception("Not implemented!")

    def test_destroy(self):
        act = ActivityFactory()

        self.client.force_login(self.user)
        response = self.client.delete(reverse('activity-detail', kwargs={'pk': act.id}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Activity.objects.filter(id=act.id).exists())

