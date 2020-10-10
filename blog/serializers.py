from typing import Any

from django.contrib.auth.models import User
from rest_framework import serializers

from blog.models import Comment, EntryEnvelope


class EntrySerializer(serializers.BaseSerializer):

    id = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()
    create_date = serializers.SerializerMethodField()
    edit_date = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    def to_representation(self, instance: Any) -> Any:
        return {
            'id': instance.entry.get('id'),
            'title': instance.entry.get('title'),
            'sections': instance.entry.get('sections'),
            'create_date': instance.entry.get('create_date'),
            'edit_date': instance.entry.get('edit_date'),
            'slug': instance.entry.get('slug'),
            'published': instance.entry.get('published'),
            'publish_date': instance.entry.get('publish_date'),
            'version': instance.entry.get('version'),
            'tags': instance.entry.get('tags'),
            '__server_generated_properties': { 'author_id': instance.author.id}
        }

    def to_internal_value(self, data: Any) -> Any:
        id = data.get('id')
        title = data.get('title')
        sections = data.get('sections')
        create_date = data.get('create_date')
        edit_date = data.get('edit_date')
        slug = data.get('slug')
        published = data.get('published')
        publish_date = data.get('publish_date')
        version = data.get('version')
        tags = data.get('tags')

        return {
            'id': id,
            'title': title,
            'sections': sections,
            'create_date': create_date,
            'edit_date': edit_date,
            'slug': slug,
            'published': published,
            'publish_date': publish_date,
            'version': version,
            'tags': tags
        }

    def update(self, instance: Any, validated_data: Any) -> Any:
        entry = validated_data
        author = self.context.get('request').user
        ee = EntryEnvelope.objects.filter(entry_id=validated_data['id']).order_by('-version')[0]
        ee.entry = entry
        ee.save()
        return ee

    def create(self, validated_data: Any) -> Any:
        entry = validated_data
        author = self.context.get('request').user
        return EntryEnvelope.objects.create(entry=entry, author=author)


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField('get_displayname')
    comments_public = serializers.SerializerMethodField('get_comments_public')

    def get_displayname(self, user):
        return user.first_name

    def get_comments_public(self, user):
        return user.profile.comments_public

    class Meta:
        model = User
        fields = ('username', 'email', 'id', 'display_name', 'comments_public')


class CommentSerializer(serializers.ModelSerializer):
    # TODO: Do we need entry here?
    entry = serializers.SerializerMethodField()
    user = UserSerializer
    user_display_name = serializers.SerializerMethodField('get_user_display_name')
    gravatar_url = serializers.SerializerMethodField('get_gravatar_url')

    # TODO: Do we need entry here?
    def get_entry(self, comment):
        return comment.entry_envelope.entry

    def get_gravatar_url(self, comment):
        return comment.user.profile.gravatar_url

    def get_user_display_name(self, comment):
        return comment.user.first_name

    class Meta:
        model = Comment
        fields = ('id', 'created_on', 'content', 'user_display_name', 'entry', 'user', 'gravatar_url')


class SyncConfigSerializer(serializers.Serializer):
    entries_endpoint = serializers.CharField()
    images_endpoint = serializers.CharField()

