# Django Start-API

Quick REST API creation.

Quick ready to use REST API based on Django and DRF, create your config file, 
launch 'startapi' and you will get:

- Standard Django project created
- All app created
 
For each app:
- Models already created and migrated
- For each model:
    - full working api (GET, POST, PUT PATCH, DELETE) (refer to: 
  https://www.django-rest-framework.org/api-guide/routers/#simplerouter) 
    - ModelViewSet already created
    - ModelSerializer already created
    - Registered urls with DefaultRouter 
    - Registered model in admin 

### Installation

    pip install django_startapi

### Quickstart

1. Create your config.yaml
2. Run 'startapi'

### Usage

This software is intented to be used to create an initial full working REST API,
based on Django and Django Rest Framework. Design apps with models inside a config file and
run django_startapi.

1. Create a config file named 'config.yaml'
2. run startapi
3. optional: python manage.py createsuperuser
4. python manage.py runserver and go to http://127.0.0.1:8000/api/

### Config file

- Add a project name used as for django-admin stratproject
- Define your apps with models, models fields are Django fields
 
> Note: Write related model name as string or put related models before 
relation  to avoid "NameError: name 'YourModel' is not defined"

Config file structure:

    project: <your_project_name>
    apps:
        <app_name>:
            <ModelName>:
                field: SomeDjangoField()
                field: SomeDjangoField()
                ...
            <ModelName>:
                field: SomeDjangoField()
                field: SomeDjangoField()
                ...
        <app_name>:
            <ModelName>:
                field: SomeDjangoField()
                field: SomeDjangoField()
                ...
            <ModelName>:
                field: SomeDjangoField()
                field: SomeDjangoField()
                ...
         ...       
  
#### Example of config file
    
    project: audiolibrary
    apps:
        band:
            Musician:
                name: CharField(max_length=40)
                surname: CharField(max_length=40)
                born_date: DateField(null=True)
            Band:
                name: CharField(max_length=100)
                author: ManyToManyField('Musician')
        album:
            Genre:
                name: CharField(max_length=100)
            Label:
                name: CharField(max_length=100)
            Album:
                name: CharField(max_length=120)
                band: ForeignKey('band.Band',  on_delete=models.DO_NOTHING)
                label: ForeignKey('Label',  on_delete=models.DO_NOTHING)
                date: DateField(null=True)

