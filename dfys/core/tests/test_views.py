from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from dfys.core.models import Category, Skill, ActivityEntry, Activity
from dfys.core.serializers import CategoryFlatSerializer
from dfys.core.tests.test_factory import CategoryFactory, UserFactory, SkillFactory, ActivityFactory, CommentFactory, \
    AttachmentFactory


class TestCategoryViewSet(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_create(self):
        cat_name = 'CatName'

        self.client.force_login(self.user)
        response = self.client.post(reverse('category-list'), data={
            'name': cat_name,
        })

        created_cat = Category.objects.get(id=response.data['id'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(created_cat.name, cat_name)
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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[cat1.pk], s.data[cat1.pk])
        self.assertEqual(response.data[cat2.pk], s.data[cat2.pk])
        self.assertEqual(response.data[cat3.pk], s.data[cat3.pk])

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
        base_category = CategoryFactory(owner=self.user, is_base_category=True)
        self.client.force_login(self.user)
        response = self.client.post(reverse('skill-list'), data={
            'name': skill_name
        })

        skill = Skill.objects.get(id=response.data['id'])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(skill.name, skill_name)
        self.assertTrue(skill.categories.filter(pk=base_category.pk).exists())

    def test_update(self):
        skill = SkillFactory(owner=self.user)
        self.client.force_login(self.user)
        response = self.client.put(reverse('skill-detail', kwargs={'pk': skill.pk}), data={
            'name': 'newName'
        })

        skill = Skill.objects.get(id=response.data['id'])

        self.assertEqual(skill.name, 'newName')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list(self):
        """
        Should provide skills flatter overview
        """
        _skill1 = SkillFactory(name='Skill1')
        _skill2 = SkillFactory(name='Skill2')
        _additional_category = CategoryFactory(owner=UserFactory(username='New user'))

        self.client.force_login(self.user)
        response = self.client.get(reverse('skill-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['skills']), 2)
        self.assertEqual(len(response.data['categories']), 4)

    def test_details(self):
        """
        Should provide skill detailed deep overview
        """
        skill1 = SkillFactory(name='Skill1')
        _skill2 = SkillFactory(name='Skill2')
        _act1 = ActivityFactory(skill=skill1)
        _act2 = ActivityFactory(skill=skill1)

        self.client.force_login(self.user)
        response = self.client.get(reverse('skill-detail', kwargs={'pk': skill1.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['categories']), 2)
        self.assertEqual(len(response.data['activities']), 2)

    def test_add_category(self):
        skill = SkillFactory()
        cat = CategoryFactory()

        self.client.force_login(self.user)
        response = self.client.post(reverse('skill-add-category', kwargs={'pk': skill.pk}), data=cat.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(skill.categories.all()), 3)

    def test_add_not_existing_category(self):
        skill = SkillFactory()

        self.client.force_login(self.user)
        response = self.client.post(reverse('skill-add-category', kwargs={'pk': skill.pk}), data=(-123))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(skill.categories.all()), 2)

    def test_remove_category(self):
        skill = SkillFactory()
        categories = skill.categories.all()

        self.client.force_login(self.user)
        response = self.client.post(reverse('skill-remove-category', kwargs={'pk': skill.pk}), data=categories[1].pk)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(skill.categories.all()), 1)
        self.assertEqual(skill.categories.all()[0].pk, categories[0].pk)

    def test_remove_not_existing_category(self):
        skill = SkillFactory()

        self.client.force_login(self.user)
        response = self.client.post(reverse('skill-remove-category', kwargs={'pk': skill.pk}), data=(-123))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(skill.categories.all()), 2)

    def test_destroy(self):
        skill1 = SkillFactory(name='Skill1')
        self.client.force_login(self.user)
        response = self.client.delete(reverse('skill-detail', kwargs={'pk': skill1.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Skill.objects.filter(pk=skill1.pk).exists())


class TestActivityViewSet(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_recent(self):
        skill = SkillFactory()
        act1 = ActivityFactory(skill=skill)
        act2 = ActivityFactory(skill=skill)
        act3 = ActivityFactory(skill=skill)

        self.client.force_login(self.user)
        response = self.client.get(reverse('activity-recent'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data[act3.id]['id'], act3.id)
        self.assertEqual(response.data[act2.id]['id'], act2.id)
        self.assertEqual(response.data[act1.id]['id'], act1.id)

    def test_details(self):
        act = ActivityFactory()
        _attachment = AttachmentFactory(activity=act)
        _comment = CommentFactory(activity=act)

        self.client.force_login(self.user)
        response = self.client.get(reverse('activity-detail', kwargs={'pk': act.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['entries']), 2)

    def test_create(self):
        skill = SkillFactory()
        cat = skill.categories.all()[0]

        self.client.force_login(self.user)

        response = self.client.post(reverse('activity-list'), data={
            'title': 'title',
            'category': cat.pk,
            'skill': skill.pk,
            'description': 'desc',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        activity = Activity.objects.get(id=response.data['id'])
        self.assertEqual(activity.title, 'title')
        self.assertEqual(activity.description, 'desc')
        self.assertEqual(activity.category, cat)
        self.assertEqual(activity.skill, skill)

    def test_destroy(self):
        act = ActivityFactory()

        self.client.force_login(self.user)
        response = self.client.delete(reverse('activity-detail', kwargs={'pk': act.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Activity.objects.filter(id=act.id).exists())


class TestEntriesViewSet(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_create(self):
        act = ActivityFactory()

        self.client.force_login(self.user)
        response = self.client.post(reverse(
            'activity-entry-list',
            kwargs={'activity_pk': act.id}),
            data={
                'comment': 'entryComment',
                'activity': act.id,
            })

        entry = ActivityEntry.objects.get(id=response.data['id'])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(entry.activity, act)
        self.assertEqual(entry.comment, 'entryComment')

    def test_update(self):
        entry = CommentFactory(comment='oldComment')

        self.client.force_login(self.user)
        response = self.client.put(reverse('activity-entry-detail', kwargs={
            'activity_pk': entry.activity.id,
            'pk': entry.id,
        }), data={
            'comment': 'newComment',
        })

        entry = ActivityEntry.objects.get(id=response.data['id'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(entry.activity, entry.activity)
        self.assertEqual(entry.comment, 'newComment')

    def test_delete(self):
        entry = CommentFactory(comment='oldComment')

        self.client.force_login(self.user)
        response = self.client.delete(reverse('activity-entry-detail', kwargs={
            'activity_pk': entry.activity.id,
            'pk': entry.id,
        }))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ActivityEntry.objects.filter(id=entry.id).exists())

    def test_list_not_allowed(self):
        act = ActivityFactory()
        self.client.force_login(self.user)
        response = self.client.get(reverse(
            'activity-entry-list',
            kwargs={'activity_pk': act.id}))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_not_allowed(self):
        entry = CommentFactory()

        self.client.force_login(self.user)
        response = self.client.get(reverse('activity-entry-detail', kwargs={
            'activity_pk': entry.activity.id,
            'pk': entry.id,
        }))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
