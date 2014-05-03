monscale
========

Small system meant to monitor services and act on them based on rules. Monscale is a Django app.

The app is able to actively monitor services and to passively listen to alerts from other systems.
The metrics monitored and the alerts received are sent to a rule engine. Based on the rules, the system
sends scale actions to the monitored systems. Metrics and actions are implemented by mappings, thus 
the development of new actions and metrics is straight-forward.

The pic below shows the a summary of the components.

![alt tag](http://blog.digitalhigh.es/wp-content/uploads/2014/05/components-1024x526.png)

Each MonitoredService is the relation of:

    - A metric.
    - A condition for that metric
    - A time the condition must be True
    - A wisdom time, this means time from the las triggered action while more actions wont be triggered.
    - An action must be triggered if the condition was True more seconds than the 
    shown by the threshold.
    
Both actions and alerts, are queued in an Redis queue, waiting for the workers to retrieve them from 
the queues. This makes the system scalable itself.


Installation
------------

The Django app can be installed just by issuing the following command, which installs every dependency

```
pip install monscale
```

The project also needs the binding from netsnmp installed on the system. Under Ubuntu the package for this 
is python-netsnmp, para instalarlo:

```
apt-get install python-netsnmp
```

Once installation is finished it's time to create the Django project under which the app will run. It
is recomended to do this by issuing the following command, as it not only creates the project, but
it also adapts its settings.py file with the configuration needed by the app.

```
monscale_deploy
```

Note that monscale uses Redis list to store some of its operational data, therefore either
install Redis and get it running, or use a predeployed Redis server. 

You'll find the settings needed to connect to the Redis server at the project 
settins.py file.

Don't forget to set the SQL DB and other configurations of your choice.

Finally populate the DB (from project's dir):

```
./manage.py syncdb
```

Usage
-----

To start the monitor daemon just issue the following command at the project's dir:

```
./manage.py evaluate_context
```

To start the actions daemon issue the following command at the project's dir:

```
./manage.py action_worker
```

To start the alerts daemon issue the following command at the project's dir:

```
./manage.py traps_worker
```

To start the development web management interface (from project's dir):

```
./manage.py runserver
```

