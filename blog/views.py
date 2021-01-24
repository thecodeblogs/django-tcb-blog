import json
import uuid
from typing import Any
from urllib.request import Request

from django.contrib.auth.models import User, AnonymousUser
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status, mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from blog.models import EntryEnvelope, Comment, Tag, View, Interaction, VisitorProfile
from blog.permissions import IsOwnerOrReadOnly, CanPostButNotRead
from blog.serializers import ( EntrySerializer, UserSerializer, CommentSerializer, SyncConfigSerializer, TagSerializer,
                              ViewSerializer, InteractionSerializer, VisitorProfileSerializer)


def get_entry_from_params(params):
    entry_id = params.get('entry', None)
    if entry_id is None:
        raise Exception("Invalid Entry")

    try:
        entry = EntryEnvelope.objects.filter(entry_id=entry_id)[0]
    except EntryEnvelope.DoesNotExist:
        raise Exception("Invalid Entry")

    return entry


class EntryViewSet(viewsets.ModelViewSet):
    serializer_class = EntrySerializer
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = 'entry_id'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['published']

    def get_queryset(self):
        return EntryEnvelope.objects.filter(defunct=False).order_by('-create_date', 'entry_id',
                                                                     '-version').distinct('create_date', 'entry_id')

    @action(detail=True, methods=['get'])
    def by_slug(self, request, entry_id):
        envelopes = EntryEnvelope.objects.filter(slug=entry_id, published=True).order_by('-create_date', 'entry_id',
                                                                         '-version').distinct('create_date', 'entry_id')
        if envelopes.count() > 0:
            serializer = self.get_serializer(instance=envelopes[0])
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        entry = get_entry_from_params(self.request.query_params)
        if self.request.user.id:
            if self.request.user.is_staff:
                return Comment.objects.filter(entry_envelope=entry)
            else:
                return Comment.objects.filter(
                    (Q(user__profile__comments_public=True) | Q(user=self.request.user))
                    & Q(entry_envelope=entry))
        else:
            return Comment.objects.filter(
                (Q(user__profile__comments_public=True))
                & Q(entry_envelope=entry))

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        envelope = get_entry_from_params(self.request.query_params)
        request.data['user'] = self.request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['entry_envelope'] = envelope
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ListUser(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk),
        except User.DoesNotExist:
            raise PermissionDenied

    def get_queryset(self):
        return self.get_object(self.request.user.id)


class SyncConfig(generics.RetrieveAPIView):
    serializer_class = SyncConfigSerializer
    def get(self, request):
        return Response(
            {
                'entries_endpoint': 'blog_api/entries/?published=true',
                'images_endpoint': '',
            },
            status=status.HTTP_200_OK
        )


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Tag.objects.all();


class ViewViewSet(mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = ViewSerializer
    permission_classes = [CanPostButNotRead]

    def get_queryset(self):
        return View.objects.all();

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        e_id = serializer.initial_data['entry']
        serializer.is_valid(raise_exception=True)

        ee = EntryEnvelope.objects.filter(entry_id=e_id)[0]
        serializer.validated_data['entry_envelope'] = ee
        serializer.validated_data['entry_id'] = ee.entry.get('id')

        if request.user.is_anonymous:
            sid_as_string = request.session.get('session_uid', None)
            if sid_as_string is None:
                sid = uuid.uuid4()
                request.session['session_uid'] = str(sid)
            else:
                sid = uuid.UUID(sid_as_string)

        if request.user.is_anonymous:
            recorded_view = View.objects.filter(entry_envelope=ee, session_uid=sid)
        else:
            recorded_view = View.objects.filter(entry_envelope=ee, user=request.user)

        # Already recorded
        if recorded_view.count() > 0:
            return Response([], status=status.HTTP_200_OK)
        else:
            self.perform_create(serializer)
            if request.user.is_anonymous:
                serializer.instance.session_uid = sid
            else:
                serializer.instance.user = request.user

            serializer.instance.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class InteractionViewSet(mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    serializer_class = InteractionSerializer
    permission_classes = [CanPostButNotRead]

    def get_queryset(self):
        return Interaction.objects.all()


class VisitorProfileViewSet(mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    serializer_class = VisitorProfileSerializer
    permission_classes = [CanPostButNotRead]

    def get_queryset(self):
        return VisitorProfile.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.is_anonymous:
            sid_as_string = request.session.get('session_uid', None)
            if sid_as_string is None:
                sid = uuid.uuid4()
                request.session['session_uid'] = str(sid)
            else:
                sid = uuid.UUID(sid_as_string)

        if request.user.is_anonymous:
            profiles = VisitorProfile.objects.filter(session_uid=sid)
        else:
            profiles = VisitorProfile.objects.filter(user=request.user)

        if profiles.count() > 0:
            exists = False
            for profile in profiles:
                if (
                    profile.name == serializer.validated_data['name'] and
                    profile.family == serializer.validated_data['family'] and
                    profile.version == serializer.validated_data['version'] and
                    profile.device == serializer.validated_data['device'] and
                    profile.os_version == serializer.validated_data['os_version']
                ):
                    exists = True
                    break
            if exists:
                return Response([], status=status.HTTP_200_OK)
            else:
                self.perform_create(serializer)

                if request.user.is_anonymous:
                    serializer.instance.session_uid = sid
                else:
                    serializer.instance.user = request.user

                serializer.instance.save()

                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            self.perform_create(serializer)

            if request.user.is_anonymous:
                serializer.instance.session_uid = sid
            else:
                serializer.instance.user = request.user

            serializer.instance.save()

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
