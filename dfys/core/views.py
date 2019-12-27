from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework.response import Response

from dfys.core.models import Category, Skill, Activity, ActivityEntry
from dfys.core.permissions import IsOwner
from dfys.core.serializers import CategoryFlatSerializer, SkillFlatSerializer, SkillDeepSerializer, \
    ActivityFlatSerializer, ActivityDeepSerializer, ActivityEntrySerializer, SkillListSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username, password = request.data['username'], request.data['password']
    user = authenticate(username=username, password=password)

    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    else:
        login(request, user)
        serialized = UserSerializer(user)
        return Response(serialized.data, status=status.HTTP_200_OK)


# TODO: Creating base categories when user is created
@api_view(['POST'])
def register(request):
    pass


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
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Skill.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SkillDeepSerializer
        return SkillFlatSerializer

    def list(self, request, *args, **kwargs):
        skills = self.get_queryset()
        skill_ids = skills.values_list('categories', flat=True)
        categories = Category.objects.filter(owner=request.user, pk__in=skill_ids)

        serializer = SkillListSerializer({
            'skills': skills,
            'categories': categories
        })

        return Response(serializer.data)

    @action(['post'], detail=True)
    def add_category(self, request, pk=None):
        category, skill = self.get_category_skill_for_action(request)
        skill.categories.add(category)
        return Response(status=status.HTTP_200_OK)

    @action(['post'], detail=True)
    def remove_category(self, request, pk=None):
        category, skill = self.get_category_skill_for_action(request)
        skill.categories.remove(category)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_category_skill_for_action(self, request):
        try:
            category_pk = request.data
            category = Category.objects.get(pk=category_pk)
        except Category.DoesNotExist:
            raise NotFound('Category not found')

        skill = self.get_object()
        return category, skill


class ActivitiesViewSet(viewsets.ModelViewSet):
    class IsActivityOwner(BasePermission):
        def has_object_permission(self, request, view, obj):
            return obj.skill.owner == request.user

    permission_classes = [IsActivityOwner]

    def get_queryset(self):
        return Activity.objects.filter(skill__owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ActivityDeepSerializer
        return ActivityFlatSerializer

    @action(detail=False)
    def recent(self, _request):
        recent_activities = Activity.objects.all().order_by('-modify_date')

        page = self.paginate_queryset(recent_activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recent_activities, many=True)
        return Response(serializer.data)


class EntriesViewSet(mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    class IsActivityOwner(BasePermission):
        def has_object_permission(self, request, view, obj):
            return obj.activity.skill.owner == request.user

    permission_classes = [IsActivityOwner]
    serializer_class = ActivityEntrySerializer

    def get_queryset(self):
        return ActivityEntry.objects.filter(activity__skill__owner=self.request.user,
                                            activity=self.kwargs['activity_pk'])
