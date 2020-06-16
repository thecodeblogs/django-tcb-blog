from django.urls import path
from rest_framework.routers import DefaultRouter

from blog.views import EntryViewSet, ListUser, CommentViewSet

router = DefaultRouter()

router.register(r'entries', EntryViewSet, basename='entries')
router.register(r'comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('me/', ListUser.as_view()),
] + router.urls
