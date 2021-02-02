==========================
TheCodeBlogs Blog Backend
==========================

Blogging made easy

Settings
-----------

These should go into your settings.py file.

.. code-block:: python

    TCB_BLOG_SETTINGS = {
        'RSS_FEED_TITLE': 'Title of the blog',
        'RSS_FEED_LINK': '/blog/',
        'RSS_FEED_ITEM_DESC_TEMPLATE': 'feed/entries.html'
    }


Quick start
-----------

1. Add "blog" to your INSTALLED_APPS setting like this

.. code-block:: python

   INSTALLED_APPS = [
   ...
   'blog',
   ]

2. Include the polls URLconf in your project urls.py like this

.. code-block:: python

   path('blog_api/', include('blog.urls')),

3. Setup a module named 'backend'

4. Using celery.py.sample as a guide, setup celery do that tasks will work

5. Run ``python manage.py migrate`` to create the blog models.

6. Start the development server and visit http://127.0.0.1:8000/admin/
     to create a poll (you'll need the Admin app enabled).

7. Visit http://127.0.0.1:8000/blog_api/ to see something.

