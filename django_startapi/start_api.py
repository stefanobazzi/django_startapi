import yaml
import os
from django.core.management import call_command
from subprocess import call

from .creator import ClassCreator, ModuleEditor, create_routers, register_apps

# TODO
import_token = """    from rest_framework.authtoken import views
urlpatterns += [
    url(r'^api-token-auth/', views.obtain_auth_token)
]"""


def load_config(name='config.yaml'):
    pwd = os.getcwd()
    cfg = os.path.join(pwd, name)
    with open(cfg, 'r') as f:
        config = yaml.safe_load(f)
    return config


class ModelClassCreator(ClassCreator):
    inherit = 'models.Model'

    def get_fields(self, cusotm_fields=None, level=1):
        fields = {k: 'models.{}'.format(v) for k, v in self.fields.items()}
        return super().get_fields(fields)


class SerializerClassCreator(ClassCreator):
    inherit = 'serializers.ModelSerializer'

    def get_class_name(self, name):
        return '{}Serializer'.format(name.capitalize())

    def __init__(self, model, fields, meta='', add_fields=False, add_meta=True,
                 add_class_decorators=False):
        super().__init__(model, fields, meta, add_fields, add_meta,
                         add_class_decorators)


class ViewSetClassCreator(ClassCreator):
    inherit = 'viewsets.ModelViewSet'

    def get_class_name(self, name):
        return '{}ViewSet'.format(name.capitalize())

    def get_fields(self, fields=None, level=1):
        default_fields = {
            'queryset': '{}.objects.all()'.format(self.model),
            'serializer_class': '{}Serializer'.format(self.model)
            # TODO
            #permission_classes = [IsAuthenticated]
        }
        return super().get_fields(default_fields)


class AdminClassCreator(ClassCreator):
    inherit = 'admin.ModelAdmin'

    def __init__(self, model, fields, meta='', add_fields=False, add_meta=False,
                 add_class_decorators=True):
        super().__init__(model, fields, meta, add_fields, add_meta,
                         add_class_decorators)

    def get_add_class_decorators(self):
        return '@admin.register({})'.format(self.model)


class SerializersEditor(ModuleEditor):
    def create_imports(self):
        models_to_import = ', '.join(self.models.keys())
        self._imports = 'from rest_framework import serializers\n'\
                        'from .models import {}\n\n'.format(models_to_import)


class ViewSetsEditor(ModuleEditor):
    def create_imports(self):
        models_to_import = ', '.join(self.models.keys())
        serialiers_to_import = ', '.join('{}Serializer'.format(m) for m in
                                         self.models.keys())
        self._imports = 'from rest_framework import viewsets\n' \
                  + 'from rest_framework.permissions import IsAuthenticated\n' \
                  + 'from .models import {}\n'.format(models_to_import) \
                  + 'from .serializers import {}\n'.format(serialiers_to_import)


class AdminEditor(ModuleEditor):
    def create_imports(self):
        self._imports = 'from .models import {}\n'.format(
            ', '.join(self.models.keys()))


def create_api(name):
    pwd = os.getcwd()
    config = load_config(name)
    project = config['project']
    apps = config['apps']
    call_command('startproject', project)
    for app, models in apps.items():
        app_path = os.path.join(pwd, project, app)
        os.mkdir(app_path)
        call_command('startapp', app, directory=app_path)
        ModuleEditor(
            name='models',
            path=app_path,
            models=models,
            class_creator=ModelClassCreator
        ).create()
        SerializersEditor(
            name='serializers',
            path=app_path,
            models=models,
            class_creator=SerializerClassCreator
        ).create()
        ViewSetsEditor(
            name='views',
            path=app_path,
            models=models,
            class_creator=ViewSetClassCreator
        ).create()
        AdminEditor(
            name='admin',
            path=app_path,
            models=models,
            class_creator=AdminClassCreator
        ).create()

    urls_py = os.path.join(pwd, project, project, 'urls.py')
    create_routers(urls_py, apps)

    # register
    #  - app
    #  - rest_framework
    #  - 'rest_framework.authtoken' if token
    settings = os.path.join(pwd, project, project, 'settings.py')
    register_apps(settings, apps)


    call(['python', '{}/manage.py'.format(project),'makemigrations'])
    call(['python', '{}/manage.py'.format(project),'migrate'])

    # TODO add tests




