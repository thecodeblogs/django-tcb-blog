from django.contrib import admin

from blog.models import ( EntryEnvelope, Profile, Comment, Tag, View,
                         Interaction, VisitorProfile )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('get_usable_email', 'id')
    def get_usable_email(self, obj):
        return obj.user.email

    get_usable_email.admin_order_field = 'user__email'
    get_usable_email.short_description = 'Email'


class EntryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['author', 'entry']}),
        ('From Blog Schema', {'fields': ['slug', 'title',
                                         'published', 'publish_date',
                                         'create_date', 'edit_date',
                                         'defunct',
                                         'future_publish_date',
                                         'future_publish_processed_on',
                                         'user_requested_future_publish',
                                         'should_publish_in_future']}),
        ('JSON', {'fields': ['entry_formatted']}),
    ]
    list_display = ('entry_id', 'title', 'get_usable_email', 'published', 'defunct')
    readonly_fields = ('title', 'entry_formatted',
                       'created_on', 'modified_on',
                       'create_date', 'edit_date', 'slug',
                       'defunct')
    search_fields = ['title', 'author__email']
    ordering = ('-edit_date', 'entry_id')

    def get_usable_email(self, obj):
        return obj.author.email

    get_usable_email.admin_order_field = 'author__email'
    get_usable_email.short_description = 'Email'

class VisitorProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['session_uid', 'user', 'name', 'family', 'version', 'device', 'language', 'os_version']}),
        ('Telemetry', {'fields': ['telemetry_formatted']})
    ]

    readonly_fields = ('telemetry_formatted',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_on', 'get_usable_email', 'get_title')
    search_fields = ['content']

    def get_title(self, obj):
        return obj.entry_envelope.title

    get_title.admin_order_field = 'entry_envelope__title'
    get_title.short_description = 'Title'

    def get_usable_email(self, obj):
        return obj.user.email

    get_usable_email.admin_order_field = 'user__email'
    get_usable_email.short_description = 'Email'


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')
    search_fields = ['label']


class ViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_usable_email', 'session_uid', 'get_title')

    def get_title(self, obj):
        return obj.entry_envelope.title

    def get_usable_email(self, obj):
        if (obj.user is not None):
            return obj.user.email
        else:
            return None

class InteractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_usable_email', 'session_uid')
    search_fields = ['content']

    def get_usable_email(self, obj):
        if (obj.user is not None):
            return obj.user.email
        else:
            return None


admin.site.register(Profile, ProfileAdmin)
admin.site.register(EntryEnvelope, EntryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(View, ViewAdmin)
admin.site.register(Interaction, InteractionAdmin)
admin.site.register(VisitorProfile, VisitorProfileAdmin)
