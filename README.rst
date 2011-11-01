=====================
Django-Sphinx-autodoc
=====================


Django is very nice in that way you can reuse a lot of applications in your
projects. It means for big projects that you'll get a long list of applications
in your settings.INSTALLED_APP.

If you're using Django with Sphinx and want to autodoc all these apps in a wink
of an eye, then this app is for you.

A good combinaison for documenting your project would be:
 - **sphinx**
 - **django-sphinx-autodoc** to generate the doc from your applications
 - **django-sphinxdoc** to integrate the sphinx doc in your website


How it works
------------

Copy the generate_autodoc.py file in your project directory, then execute it.

It will scrape all your .py files in each application listed by INSTALLED_APP,
then add automodules in your DS_ROOT/modules.rst.

You will then see your applications grouped in 2 different categories:

- **internal application** is an application located in your project directory
- **external application** is an app which is somewhere in your pythonpath
  (preferably in your virtualenv)

Good Practices
--------------

Add a docstring in your application's __init__.py file to describe it.
django-sphinx-autodoc will automatically scrape it for you.


Settings
--------

You can modify some of the settings used by django-sphinx-autodoc:

- **DS_ROOT**: root path for documentation (default to project_dir/doc)
- **DS_MASTER_DOC**: name of your master document (default to "index.rst")
- **DS_FILENAME**: name for the modules (default to "auto_modules.rst")
- **DS_EXCLUDED_APPS**: list of applications to exclude (default to [])
- **DS_EXCLUDED_MODULES**: list of files to exclude (default to ["__init__.py"])


TODO
----

- Write tests
- improve the not_relevant stuff to auto exclude a file without class or def
- Django command extension to update the autodoc

ADDED SPECIAL CASE FUNCTIONALITY
--------------------------------

If you want to generated the docs automatically and do not want to have to have this 
file living at your project root directory, you can use it in the following way.

Install this module via PIP or have it somewhere on your Python Path.

In you Sphinx conf.py file, usually found in the docs/ directory, add:
::

    # Link into generate autodocs via Django-Sphinx-Autodoc
    try:
        import generate_autodoc
    except ImportError:
        print ("There was an issue importing the Autodoc function module.")
    
    PROJECT_DIR = os.path.abspath( os.path.join(os.path.dirname(__file__), "..") )
    PROJECT_DIRNAME = PROJECT_DIR.split('/')[-1]
    project_dir = lambda p: os.path.abspath( os.path.join(PROJECT_DIR, p) )

    DJANGO_AUTODOC_SETTINGS = {
        'PROJECT_ROOT': PROJECT_DIR,
        'DOCS_ROOT': project_dir('docs'),
        'MASTER_DOC': "index.rst",
        'FILENAME': "api/ref.rst",
        'EXCLUDED_APPS': [
            'grappelli.dashboard',
            'grappelli',
            'filebrowser',
            'django.contrib.admin',
            'django.contrib.admindocs',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.databrowse',
            'django.contrib.messages',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.staticfiles',
            'south',
        ],
        'EXCLUDED_MODULES': ["__init__.py", ],
    }
    generate_autodoc.generate_autodocs(DJANGO_AUTODOC_SETTINGS)


Now, when you run ``make HTML`` as the conf.py file is parsed by Sphinx, the docs will be 
generated.

Remember to include a link in your TOC somewhere to this file.  For example, in this case I have

.. parsed-literal::

    API/Reference Docs
    ------------------

    .. toctree::
       :maxdepth: 2
       api/ref


   