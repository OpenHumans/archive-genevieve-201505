django_celery_fileprocess_example
=================================

This project is a demo of implementing Celery and Django to perform
asynchronous processing of an uploaded file. In this demo, a file is
uploaded, processed with python's gzip module to create a compressed
version, and the resulting .gz file is made available for download.

Installation
------------
These instructions were written for Ubuntu Linux 13.10 or 14.04.

### Clone the Git repository ###

Navigate to the directory you want to have the code in, and clone the
repository with: `git clone git://github.com/madprime/django_celery_fileprocess_example`.

### Install pip, virtualenv, and virtualenvwrapper ###

1. **(Root user action)** Install pip: `sudo apt-get install python-pip`
2. **(Root user action)** Use pip to install virtualenv and
virtualenvwrapper: `sudo pip install virtualenv virtualenvwrapper`.

### Set up virtualenv and virtualenvwrapper ###

1. Make a directory to store your virtual environments:
`mkdir ~/.virtualenvs`
2. To make virtualenv and virtualenvwrapper commands work in future
terminals, add the following to your bashrc (or zshrc, as appropriate):
`export WORKON_HOME=$HOME/.virtualenvs` and
`source /usr/local/bin/virtualenvwrapper.sh`.

### Make a virtual environment and install required Python packages ###

If you open a new terminal you should now be able to access the
virtualenvwrapper commands listed below.

If you aren't familiar with pip and virtualenv: these are standard tools
in Python development, greatly facilitating package management. Whenever
working on this software you should do so within the virtual environment
(e.g. after performing step 2 below).

1. Create a new virtual environment for working on this code:
`mkvirtualenv django_celery_fileprocess`
2. Start using this virtual environment:
`workon django_celery_fileprocess`
3. Navigate to top directory in this project. (One of the subdirectories
should be `file_process`.) Install the Python packages required for
development with `pip install -r requirements.txt`.

### Set up RabbitMQ ###

Celery requires a message broker. This broker acts a middleman sending
and receiving messages to Celery workers who in turn process tasks as
they receive them. Celery recommends using RabbitMQ, an open source
tool.

1. **(Root user action)** Install RabbitMQ:
`sudo apt-get install rabbitmq-server`
2. Ubuntu automatically begins running a rabbit server in the background
once this is installed.
3. **(Root user action)** Starting the server is as simple as:
`sudo rabbitmq-server` (runs in the foreground), or you can start it in
the background with `sudo rabbitmq-server -detached`. To stop the server
use `sudo rabbitmqctl stop`.

### Launch Celery ###

To launch Celery, from the project's base directory run:
`celery -A django_celery_fileprocess_example worker -l info`
(this runs in the foreground)

### Initialize and run Django ###

In a new terminal, start your virtual environment (with
`workon django_celery_fileprocess`) and run the following in the
project's base directory to initialize the database and then run a
local Django server.

1. `python manage.py syncdb`
2. `python manage.py runserver`

If you're running this locally, you'll be able to navigate to
`http://127.0.0.1:8000` in a web browser. This demo will allow you to
upload a file to the site, it will then asynchronously create a
gzipped version of that file. Once the gzip is done, a link to the
gzipped file will appear.
