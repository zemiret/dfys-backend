from rest_framework import serializers

from dfys.core.models import Category, Skill, Activity, ActivityEntry

# TODO: COnsider which fields should be read_only


class ActivityEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityEntry
        exclude = ('activity', )


class ActivityFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'


class ActivityDeepSerializer(serializers.ModelSerializer):
    entries = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = '__all__'

    def get_entries(self, instance):
        entries = instance.activityentry_set.all().order_by('-modify_date')
        return ActivityEntrySerializer(entries, many=True).data

    def create(self, validated_data):
        raise serializers.ValidationError('Activity cannot be created via ActivityDeepSerializer')

    def update(self, instance, validated_data):
        raise serializers.ValidationError('Activity cannot be updated via ActivityDeepSerializer')


class CategoryFlatSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Category
        fields = '__all__'


class CategoryInSkillSerializer(serializers.ModelSerializer):
    activities = ActivityFlatSerializer(read_only=True, many=True, source='activity_set')

    class Meta:
        model = Category
        exclude = ('owner', 'is_base_category')


class SkillFlatSerializer(serializers.ModelSerializer):
    categories = CategoryFlatSerializer(read_only=True, many=True)
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Skill
        fields = '__all__'

    def create(self, validate_data):
        base_categories = Category.objects.filter(owner=validate_data['owner'], is_base_category=True)
        skill = Skill.objects.create(**validate_data)
        skill.categories.add(*base_categories)
        return skill


class SkillDeepSerializer(serializers.ModelSerializer):
    categories = CategoryInSkillSerializer(read_only=True, many=True)

    class Meta:
        model = Skill
        exclude = ('owner', )

    def create(self, validated_data):
        raise serializers.ValidationError('Skill cannot be created via DeepSkillSerializer')

    def update(self, instance, validated_data):
        raise serializers.ValidationError('Skill cannot be updated via DeepSkillSerializer')
