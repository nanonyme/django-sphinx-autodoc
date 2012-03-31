#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This program scrapes all your .py files in each application
listed by INSTALLED_APP, then add automodules in your DS_ROOT/modules.rs
"""
from __future__ import with_statement
#from python
import os
import re


def add_lf(line_list):
    """Append line feed \n to all elements of the given list"""
    return ["%s\n" % line for line in line_list]


class Modules(object):
    """
    auto_modules.rst file to store all the apps automodules
    """

    def __init__(self, config):
        self.internal_apps = []
        self.external_apps = []
        self.fname = config['FILENAME']
        self.in_index = None

    def write(self):
        """Write the created list in the new file"""
        with open("%s.rst" % self.fname, "w+") as output_file:
            title = "Internal Applications"
            symbol_line = "=" * len(title)
            l_file = add_lf([symbol_line, title, symbol_line, "", ""])
            l_file.extend(self.internal_apps)
            title = "External Applications"
            external_title = add_lf([symbol_line, title,
                                     symbol_line, "", ""])
            l_file.extend(external_title)
            l_file.extend(self.external_apps)
            output_file.writelines(l_file)

    def add_to_toctree(self, toctree):
        """
        Verify that a "auto_modules" file is in the toctree, and append it
        otherwise
        """
        re_m = re.compile(self.fname)
        self.in_index = re_m.findall("".join(toctree)) and True or False
        # Now that we know the title, append it at the beginning of the file

    def add_app(self, app):
        """template of application autodoc"""

        if not app.path:
            # App couldn't be documented
            # template += ".. error:: This app couldn't be documented\n\n"
            # TODO Most themes doesn't style error, need to custom it
            template = ".. warning:: '%s' couldn't be documented\n\n"
            template = template % app.name  # NOQA
        else:
            # Write the name of the application
            template = add_lf([app.name, "=" * len(app.name), ""])

            if app.has_description():
                # Description of the application if it exists
                template += ".. automodule:: %s\n\n" % app.name
            if not app.modules:
                template += ".. warning:: This app has no documentation\n\n"

            # Write an automodule for each of its modules
            for module in app.modules:
                template += add_lf([
                    # title of the module
                    module, "-" * len(module), "",
                    # automodule
                    ".. automodule:: %s.%s" % (app.name, module),
                    "    :deprecated:",
                    "    :members:",
                    "    :undoc-members:",
                    "    :show-inheritance:", "",
                ])
        if app.is_internal:
            self.internal_apps.extend(template)
        else:
            self.external_apps.extend(template)


class App(object):
    """Application with its name and the list of python files it contains"""

    def __init__(self, name, config):
        self.name = name
        self.is_internal = self.name in os.listdir(config['PROJECT_ROOT'])
        self.excluded_modules = config['EXCLUDED_MODULES']
        self.path = self.get_path()
        self.modules = self.get_modules()
        

    def get_path(self):
        """return absolute path for this application"""
        try:
            path = __import__(self.name).__path__[0]
            splited_name = self.name.split(".")
            if len(splited_name) > 1:
                path = os.path.join(path, *splited_name[1:])
            return path
        except ImportError:
            print "The application %s couldn't be autodocumented" % self.name
            return False

    def get_modules(self):
        """Scan the repository for any python files"""
        if not self.path:
            return []
        # Move inside the application
        os.chdir(self.path)

        modules = [f.split(".py")[0] for f in os.listdir(".") if f not
                   in self.excluded_modules and f.endswith(".py")]
        # Remove all irrelevant modules. A module is relevant if he
        # contains a function or class
        not_relevant = []
        for module in modules:
            with open("%s.py" % module, "r") as f_module:
                content = f_module.read()
            keywords = ["def", "class"]
            relevant = sum([value in content for value in keywords])
            if not relevant:
                not_relevant.append(module)
                print "%s.%s not relevant, removed" % (self.name, module)
        for module in not_relevant:
            modules.remove(module)
        return modules


    def has_description(self):
        """Get the application docstring from __init__.py if it exists"""
        with open("%s/__init__.py" % self.path, "r") as f_init:
            content = f_init.read()
        if '"""' in content or "'''" in content:
            return True
        return False


def generate_autodocs(config):
    """Main entrypoint
    :param config: dictionary that contains configurations
    """
    # Create a file for new modules
    f_modules = Modules(config)
    # Write all the apps autodoc in the newly created file
    l_apps = set(config['INSTALLED_APPS']) - set(config['EXCLUDED_APPS'])
    for name in l_apps:
        f_modules.add_app(App(name, config))

    # Go to the doc directory and open the index
    os.chdir(config['DOCS_ROOT'])
    try:
        with open(config['MASTER_DOC'], "r") as f_index:
            l_index = f_index.readlines()
            # Set the file name for modules
            f_modules.add_to_toctree(l_index)
    except IOError:
        raise IOError("No file %s/%s exists, please fix it" %
             (config['DOCS_ROOT'], config['MASTER_DOC']))

    # Write the modules file
    f_modules.write()

    # append the new file name to the index.rst
    if not f_modules.in_index:
        for i, line in enumerate(l_index):
            if ":maxdepth: 2" in line:
                l_index.insert(i + 2, "    %s\n" % f_modules.fname)
                break
    with open(config['MASTER_DOC'], "w") as f_index:
        f_index.writelines(l_index)

if __name__ == '__main__':
    
    HERE = os.path.realpath(os.path.dirname(__file__))

    # from project
    try:
        # Get the list of applications from the settings
        import settings
        from django.core.management import setup_environ
        setup_environ(settings)  # some apps will fail to load without some
                                 # specific settings
    except ImportError:
        raise ImportError("The script should be run from the project root")

    CONFIG = {
        'PROJECT_ROOT': HERE,
        'DOCS_ROOT': os.path.join(HERE, "doc"),
        'MASTER_DOC': "index.rst",
        'FILENAME': "auto_modules",
        'INSTALLED_APPS': settings.INSTALLED_APPS,
        'EXCLUDED_APPS': [],
        'EXCLUDED_MODULES': ["__init__.py", ],
    }
    
    
    DJANGO_AUTODOC_SETTINGS = getattr(settings, "DJANGO_AUTODOC_SETTINGS", {})
    # Update the values to pass for this instance
    for key in DJANGO_AUTODOC_SETTINGS:
        CONFIG[key] = DJANGO_AUTODOC_SETTINGS[key]
        
    generate_autodocs(CONFIG)
