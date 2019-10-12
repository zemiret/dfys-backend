from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from dfys.core.models import Category, Skill, Activity, ActivityEntry
from dfys.core.permissions import IsOwner
from dfys.core.serializers import CategoryFlatSerializer, SkillFlatSerializer, SkillDeepSerializer, \
    ActivityFlatSerializer, ActivityDeepSerializer, ActivityEntrySerializer


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

    @action(detail=True, methods=['post'])
    def entries(self, request, pk=None):
        activity = self.get_object()
        data = request.data

        data['activity'] = activity.id

        serializer = ActivityEntrySerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @entries.mapping.put
    def update_entry(self, request, pk=None, *args, **kwargs):
        # TODO: Make this work somehow
        activity = self.get_object()
        data = request.data

        data['activity'] = activity.id

        existing_entry_id = int(kwargs['entry_id'])
        existing_entry = ActivityEntry.objects.get(id=existing_entry_id)
        serializer = ActivityEntrySerializer(instance=existing_entry, data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
