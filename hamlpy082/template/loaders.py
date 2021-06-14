import os

from django.template import TemplateDoesNotExist
from django.template.loaders import filesystem, app_directories

from hamlpy import hamlpy
from hamlpy.template.utils import get_django_template_loaders


def get_haml_loader(loader):
    class Loader(loader.Loader):
        def get_contents(self, origin):
            # >= Django 1.9
            contents = super(Loader, self).get_contents(origin)
            name, _extension = os.path.splitext(origin.template_name)
            # os.path.splitext always returns a period at the start of extension
            extension = _extension.lstrip('.')

            if extension in hamlpy.VALID_EXTENSIONS:
                hamlParser = hamlpy.Compiler()
                return hamlParser.process(contents)

            return contents

        def load_template_source(self, template_name, *args, **kwargs):
            # < Django 1.9
            _name, _extension = os.path.splitext(template_name)

            for extension in hamlpy.VALID_EXTENSIONS:
                try:
                    haml_source, template_path = super(Loader, self).load_template_source(
                        self._generate_template_name(_name, extension), *args, **kwargs
                    )
                except TemplateDoesNotExist:
                    pass
                else:
                    hamlParser = hamlpy.Compiler()
                    html = hamlParser.process(haml_source)

                    return html, template_path

            raise TemplateDoesNotExist(template_name)

        load_template_source.is_usable = True

        def _generate_template_name(self, name, extension="hamlpy"):
            return "%s.%s" % (name, extension)

    return Loader


haml_loaders = dict((name, get_haml_loader(loader))
        for (name, loader) in get_django_template_loaders())


HamlPyFilesystemLoader = get_haml_loader(filesystem)
HamlPyAppDirectoriesLoader = get_haml_loader(app_directories)
