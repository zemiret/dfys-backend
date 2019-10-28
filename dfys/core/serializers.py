from abc import ABC

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from dfys.core.models import Category, Skill, Activity, ActivityEntry


ADD_MODIFY_FIELDS = ['add_date', 'modify_date']


class DictSerializer(serializers.ListSerializer, ABC):
    """
    Overrides default ListSerializer to return a dict with a custom field from
    each item as the key. Makes it easier to normalize the data so that there
    is minimal nesting. dict_key defaults to 'pk' but can be overridden.
    Adapted from: https://ewp.gma.mybluehost.me/2018/11/17/normalize-your-django-rest-serializers/
    (credits to the author of the post)
    """
    dict_key = 'id'

    @property
    def data(self):
        """
        Overridden to return a ReturnDict instead of a ReturnList.
        """
        ret = super(serializers.ListSerializer, self).data
        return ReturnDict(ret, serializer=self)

    def to_representation(self, data):
        """
        Converts the data from a list to a dictionary.
        """
        items = super(DictSerializer, self).to_representation(data)
        return {item[self.dict_key]: item for item in items}


class DisableCreateUpdate:
    def update(self, instance, validated_data):
        raise serializers.ValidationError('This object type cannot be created via {}'.format(self.__class__.__name__))

    def create(self, validated_data):
        raise serializers.ValidationError('This object type be created via {}'.format(self.__class__.__name__))


class ActivityEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityEntry
        fields = '__all__'
        ordering = ['modify_date']
        read_only_fields = ADD_MODIFY_FIELDS
        list_serializer_class = DictSerializer
        extra_kwargs = {
            'activity': {'write_only': True, 'required': False}
        }


class ActivityFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'
        read_only_fields = ADD_MODIFY_FIELDS
        list_serializer_class = DictSerializer


class ActivityDeepSerializer(serializers.ModelSerializer, DisableCreateUpdate):
    entries = ActivityEntrySerializer(many=True,
                                      source='activityentry_set',
                                      read_only=True)

    class Meta:
        model = Activity
        fields = '__all__'
        read_only_fields = ADD_MODIFY_FIELDS


class CategoryFlatSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['is_base_category']
        list_serializer_class = DictSerializer


class CategoryInSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('owner', 'is_base_category')
        list_serializer_class = DictSerializer


class SkillFlatSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    categories = serializers.PrimaryKeyRelatedField(required=False, many=True, read_only=True)

    class Meta:
        model = Skill
        fields = '__all__'
        read_only_fields = ['add_date']
        list_serializer_class = DictSerializer

    def create(self, validate_data):
        base_categories = Category.objects.filter(owner=validate_data['owner'], is_base_category=True)
        skill = Skill.objects.create(**validate_data)
        skill.categories.set(base_categories)
        return skill


class SkillListSerializer(DisableCreateUpdate, serializers.Serializer):
    skills = SkillFlatSerializer(many=True, read_only=True)
    categories = CategoryFlatSerializer(many=True, read_only=True)


class SkillDeepSerializer(serializers.ModelSerializer):
    categories = CategoryInSkillSerializer(read_only=True, many=True)
    activities = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        exclude = ('owner', )
        read_only_fields = ['add_date']

    def get_activities(self, skill):
        activities = Activity.objects.filter(skill=skill)
        return ActivityFlatSerializer(activities, many=True, context={'request': self.context['request']}).data

    def create(self, validated_data):
        raise serializers.ValidationError('Skill cannot be created via {}'.format(self.__class__.__name__))

    def update(self, instance, validated_data):
        raise serializers.ValidationError('Skill cannot be created via {}'.format(self.__class__.__name__))
