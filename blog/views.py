from typing import Any
from urllib.request import Request

from django.contrib.auth.models import User, AnonymousUser
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from blog.models import EntryEnvelope, Comment
from blog.permissions import IsOwnerOrReadOnly
from blog.serializers import EntrySerializer, UserSerializer, CommentSerializer, SyncConfigSerializer


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
        request.data['entry_envelope'] = envelope.id
        request.data['user'] = self.request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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

