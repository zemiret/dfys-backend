import factory
from django.core.files.uploadedfile import SimpleUploadedFile

from factory.django import DjangoModelFactory

from dfys.core.models import ActivityEntry


class UserFactory(DjangoModelFactory):
    class Meta:
        model = 'auth.User'
        django_get_or_create = ('username',)

    username = 'testuser'


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = 'core.Category'

    owner = factory.SubFactory(UserFactory)
    name = 'TestCategory'


class SkillFactory(DjangoModelFactory):
    class Meta:
        model = 'core.Skill'

    owner = factory.SubFactory(UserFactory)
    name = 'TestSkill'

    @factory.post_generation
    def add_categories(self, create, extracted, **kwargs):
        self.categories.add(CategoryFactory(name='TestCategory1', is_base_category=True))
        self.categories.add(CategoryFactory(name='TestCategory2', is_base_category=True))


class ActivityFactory(DjangoModelFactory):
    class Meta:
        model = 'core.Activity'

    title = 'TestActivity'
    category = factory.SubFactory(CategoryFactory)
    skill = factory.SubFactory(SkillFactory)
    description = ''


class AttachmentFactory(DjangoModelFactory):
    class Meta:
        model = 'core.ActivityEntry'

    attachment_content = None
    activity = factory.SubFactory(ActivityFactory)
    type = ActivityEntry.ATTACHMENT


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = 'core.ActivityEntry'

    comment_content = 'comment'
    activity = factory.SubFactory(ActivityFactory)
    type = ActivityEntry.COMMENT
