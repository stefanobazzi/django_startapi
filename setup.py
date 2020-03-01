import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-startapi", # Replace with your own username
    version="0.0.2.dev2",
    author="Stefano Bazzi",
    author_email="stefanobazzi@yahoo.it",
    description="Quick REST API creation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stefanobazzi/django_startapi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=['bin/startapi'],
    python_requires='>=3.6',
    install_requires=[
        "Django>=3.0.3",
        "djangorestframework>=3.11.0",
        "PyYAML>=5.3",
    ]
)
