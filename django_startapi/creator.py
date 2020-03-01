import os
from string import Template

from .insert import Insert

MODULE = "$imports\n\n$classes"
CLASS = "$decorators\nclass $class_name$inherit:\n$class_attrs\n$meta\n"
ATTR = "{spaces}{attr} = {value}\n"
META = "    class Meta:\n$meta_attrs"


def join_attributes(attrs, level=1):
    spaces = '    ' * level
    return ''.join(ATTR.format(spaces=spaces, attr=a, value=v)
                   for a, v in attrs.items())


def create_routers(path, apps):
    imports = 'from rest_framework.authtoken.views import obtain_auth_token\n'\
              'from rest_framework.routers import DefaultRouter\n'\
              'from django.urls import include\n'\
              'from django.contrib import admin\n'
    routers = 'router = DefaultRouter()\n'
    for app, models in apps.items():
        viewsets = []
        for model in models.keys():
            viewset = '{}ViewSet'.format(model)
            viewsets.append(viewset)
            routers += 'router.register(r"{}", {})\n'.format(model.lower(),
                                                             viewset)
        imports += 'from {}.views import {}\n'.format(app, ', '.join(viewsets))
    routers += '\n'
    urls = "    path('api/', include(router.urls)),\n"\
           "    path('api-auth/', include('rest_framework.urls', "\
           "namespace='rest_framework')),\n"\
           "    path('token/', obtain_auth_token)\n"
    with Insert(path) as insert:
        insert.after('"""', imports, last=True)
        insert.before('urlpatterns = [', routers)
        insert.after("    path('admin/'", urls)


def register_apps(path, apps):
    apps_config = ["    '{}.apps.{}Config',\n".format(app, app.capitalize())
                   for app in apps.keys()]
    installed_apps = "    'rest_framework',\n    'rest_framework.authtoken',\n"\
                     + "".join(apps_config)
    with Insert(path) as insert:
        insert.after("    'django.contrib.staticfiles'", installed_apps)


class ClassCreator:
    inherit = 'object'

    def __init__(self, model, fields, meta='', add_fields=True, add_meta=False,
                 add_class_decorators=False):
        self._serializer = fields.pop('_serializer', None)
        self._viewset = fields.pop('_viewset', None)
        self.model = model
        self.fields = fields
        self.add_fields = add_fields
        self.add_meta = add_meta
        self.meta = meta
        self.add_class_decorators = add_class_decorators

        self.template = Template(CLASS)

    def get_class_name(self, name):
        return name.capitalize()

    def get_fields(self, cusotm_fields=None, level=1):
        return join_attributes(cusotm_fields or self.fields, level)

    def create(self, name, fields='', meta_attrs=''):
        #class_attrs = class_attrs or self.class_attrs
        #meta_attrs = meta_attrs or self.meta_attrs
        meta = ''
        if self.inherit:
            self.inherit = "(%s)" % self.inherit
        if self.add_fields:
            fields = self.get_fields(fields)
        if self.add_meta:
            meta = self.get_meta()
        if not fields and not meta:
            fields = '    pass'
        cls = self.template.substitute(
            decorators=self.get_add_class_decorators(),
            class_name=self.get_class_name(name),
            inherit=self.inherit,
            class_attrs=fields,
            meta=meta
        )
        return cls

    def get_meta(self, meta_attrs=''):
        meta_attrs = meta_attrs or {'model': self.model, 'fields': "'__all__'"}
        meta_template = Template(META)
        meta_attrs = join_attributes(meta_attrs, level=2)
        meta = meta_template.substitute(meta_attrs=meta_attrs)
        return meta

    def get_add_class_decorators(self):
        return ''


class ModuleEditor:
    def __init__(self, name, path, models, class_creator=ClassCreator):
        self.name = '{}.py'.format(name) if not name.endswith('.py') else name
        self.path = path
        self._classes = None
        self._imports = None
        self.models = models
        self.ClsCreator = class_creator

    def create(self):
        self.create_imports()
        self.create_classes()
        self.save()

    def save(self):
        path = os.path.join(self.path, self.name)
        with Insert(path) as insert:
            self.insert_imports(insert)
            self.insert_classes(insert)

    def insert_imports(self, insert):
        insert.at_index(0, self._imports)

    def insert_classes(self, insert):
        insert.append(self._classes)

    def create_imports(self):
        self._imports = ''

    def create_classes(self):
        self._classes = []
        for model, fields in self.models.items():

            # TODO
            serializers = fields.pop('_serializer', None)
            viewset = fields.pop('_viewset', None)

            class_creator = self.ClsCreator(model, fields)
            cls = class_creator.create(model)
            self._classes.append(cls)
