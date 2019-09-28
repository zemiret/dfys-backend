from rest_framework import serializers

from dfys.core.models import Category, Skill


class CategorySerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Category
        fields = '__all__'


class FlatSkillSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(read_only=True, many=True)
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Skill
        fields = '__all__'

    def create(self, validate_data):
        base_categories = Category.objects.filter(owner=validate_data['owner'], is_base_category=True)
        skill = Skill.objects.create(**validate_data)
        skill.categories.add(*base_categories)
        return skill


class DeepSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
