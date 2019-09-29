import factory

from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = 'auth.User'
        django_get_or_create = ('username', )

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
        self.categories.add(CategoryFactory(name='TestCategory1'))
        self.categories.add(CategoryFactory(name='TestCategory2'))


class ActivityFactory(DjangoModelFactory):
    class Meta:
        model = 'core.Activity'

    title = 'TestActivity'
    category = factory.SubFactory(CategoryFactory)
    skill = factory.SubFactory(SkillFactory)
    description = ''
