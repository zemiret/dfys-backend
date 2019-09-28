from django.shortcuts import render
# from django.contrib.auth.decorators import login_required

# Create your views here.
# @login_required
from rest_framework import viewsets
from rest_framework import permissions

from dfys.core.models import Category, Skill
from dfys.core.permissions import IsOwner
from dfys.core.serializers import CategorySerializer, FlatSkillSerializer


def index(request):
    return render(request, 'core/index.html')


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)


class SkillViewSet(viewsets.ModelViewSet):
    serializer_class = FlatSkillSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Skill.objects.filter(owner=self.request.user)

