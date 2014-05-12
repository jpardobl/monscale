monscale
========

Small system meant to monitor services and act on them based on rules. Monscale is a Django app.

The app is able to actively monitor services and to passively listen to alerts from other systems.
The metrics monitored and the alerts received are sent to a rule engine. Based on the rules, the system
sends scale actions to the monitored systems. Metrics and actions are implemented by mappings, thus 
the development of new actions and metrics is straight-forward.

The pic below shows the a summary of the components.

![alt tag](http://blog.digitalhigh.es/wp-content/uploads/2014/05/components.png)

Objects explanation
-------------------

Infrastructure is splitted in pieces. Each piece relates to the portion of infrastructure that scales up or down
based on a certain behaviour and a certain automatic operation. For example, a grid of web servers that host
the the presentation tier for the same application, can be monitored against the same metric (response time) and
in case it needs to scale, this is done by adding/subtracting web nodes. This behaviour is represented by the
InfrastructureService Model, which holds the name of the piece of infrastructure, the maximum and minimum nodes it
is allowed to scale up and down respectively.

Each ServiceInfrastructure is related to one or more MonitoredService obj, which is the relation of:

    - A set of thresholds, each means:
         - metric to monitor.
         - A condition for that metric
         - A time the condition must be in alarm state
    - A wisdom time, this means time from the last triggered action while more actions wont be triggered.
    - A set of actions (ScaleAction model) that must be triggered if the condition was True more seconds than the
    shown by the threshold.

Every metric read is passed through the rule engine in order to make a scaling decision. If the rules say so, an
ScaleAction is queued for execution.

Finally we have traps. Al the above explanation is about the active role of the system, by which it asks the
monitored services about their metrics. Traps are related to its passive role. The system listens for alerts from
other systems. When an alert is received it is passed through the same rule engine as read metrics.


Both actions and alerts are queued in Redis queues, waiting for the workers to retrieve them from
the queues. This makes the system really scalable itself.

Featured Service Escalation Actions
-----------------------------------

 - Cloudforms 3.0:
      - Send virtual machine provision request
      - Send virtual machine decomition request
 - F5 Icontrol:
      - Scale up/down load balancer pools
 - Amazon Web Services
      - Publish messages to SNS topic
          
Featured Monitoring Metrics
--------------------------

 - Retrieve SNMPv1 and SNMPv2 OID
 - Retrieve Redis list length
 - Retrieve HTTP response
 
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

