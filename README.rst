=====
TheCodeBlogs Blog Backend
=====

Quick start
-----------

1. Add "blog" to your INSTALLED_APPS setting like this::

   INSTALLED_APPS = [
   ...
   'blog',
   ]

2. Include the polls URLconf in your project urls.py like this::

   path('blog_api/', include('blog.urls')),

   3. Run ``python manage.py migrate`` to create the blog models.

   4. Start the development server and visit http://127.0.0.1:8000/admin/
         to create a poll (you'll need the Admin app enabled).

   5. Visit http://127.0.0.1:8000/blog_api/ to see something.
