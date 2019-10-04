from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from dfys.core.models import Category, Skill
from dfys.core.permissions import IsOwner
from dfys.core.serializers import CategoryFlatSerializer, SkillFlatSerializer, SkillDeepSerializer, ActivityFlatSerializer


@login_required
def index(request):
    return render(request, 'core/index.html')


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategoryFlatSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        if self.get_object().is_base_category:
            raise ValidationError(detail='Base category cannot be deleted')

        return super().destroy(request, *args, **kwargs)


class SkillViewSet(viewsets.ModelViewSet):
    serializer_class = SkillFlatSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Skill.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SkillDeepSerializer
        return SkillFlatSerializer

# TODO: Consider how to GET activity "details".
# Maybe just an API view that will return all the activity entries given the activity id
