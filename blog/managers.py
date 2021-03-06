from django.db.models import QuerySet, Manager, Q

class EntriesQuerySet(QuerySet):
    def only_published(self):
        return self.filter(Q(published=True) & Q(defunct=False))
    def for_author(self, handle):
        return self.filter(author__handle=handle)
    def with_tags(self, tags):
        return self.filter(tag_set__in=tags)


class DefaultEntriesManager(Manager):

    def get_queryset(self):
        return EntriesQuerySet(self.model, using=self._db)

    def only_published(self):
        return self.get_queryset().only_published()

    def for_author(self, handle):
        return self.get_queryset().for_author(handle)

    def with_tags(self, tags):
        return self.get_queryset().with_tags(tags)


class CommentQuerySet(QuerySet):

    def public(self):
        return self.filter(user__profile__comments_public=True)

    def approved(self):
        return self.filter(approved=True)


class DefaultCommentManager(Manager):
    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db)

    def public(self):
        return self.get_queryset().public();

    def approved(self):
        return self.get_queryset().approved();
