from django.contrib import admin

from blog.models import ( EntryEnvelope, Profile, Comment, Tag, View,
                         Interaction, VisitorProfile )


class EntryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['author', 'entry']}),
        ('From Blog Schema', {'fields': ['slug', 'title',
                                         'published', 'publish_date',
                                         'create_date', 'edit_date',
                                         'defunct']}),
        ('JSON', {'fields': ['entry_formatted']}),
    ]
    list_display = ('id', 'entry_id', 'title', 'published', 'defunct')
    readonly_fields = ('title', 'entry_formatted',
                       'created_on', 'modified_on',
                       'create_date', 'edit_date', 'slug',
                       'defunct')
    ordering = ('-edit_date', 'entry_id')

class VisitorProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['session_uid', 'user', 'name', 'family', 'version', 'device', 'language', 'os_version']}),
        ('Telemetry', {'fields': ['telemetry_formatted']})
    ]

    readonly_fields = ('telemetry_formatted',)


admin.site.register(Profile)
admin.site.register(EntryEnvelope, EntryAdmin)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(View)
admin.site.register(Interaction)
admin.site.register(VisitorProfile, VisitorProfileAdmin)
