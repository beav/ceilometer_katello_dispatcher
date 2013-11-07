ceilometer_katello_dispatcher
=============================

This is a ceilometer dispatcher that feeds instance data directly into Katello. Systems do not have to register with subscription-manager in order to show up. This allows non-RHEL systems to show up as consumers in Katello.

If a system does register with subscription-manager using the existing UUID, it will re-use the existing consumer record. When the system is terminated, its consumer record will disappear.

requirements
------------
* python-rhsm 1.8.9 or later
* katello of a recent vintage that includes hash 5a12757


to set up an rdo instance in a vm
---------------------------------

 * find a fedora machine
 * if intel, run "rmmod kvm_intel; modprobe kvm_intel nested=y"
 * create a rhel or centos vm. 4GB mem and 2 CPU works ok.
 * on the VM: follow http://openstack.redhat.com/QuickStartLatest or http://openstack.redhat.com/Quickstart
 * on the VM: edit /etc/rhsm/rhsm.conf to point to your katello system
 * on the VM: install the ceilometer_katello_dispatcher rpm, and edit /etc/ceilometer/ceilometer.conf

        [dispatcher_katello]
        default_owner = ACME_Corporation

        [collector]
        dispatchers = katello 
        dispatchers = database # this needs to be defined if we are also defining the katello dispatcher

 * on the VM: service openstack-ceilometer-collector restart
 * from the horizon dashboard, fire up an instance. Cirros works fine for this.
 * you should see katello-related output in /var/log/ceilometer/collector.log

to install without RPM: python ./setup.py install; service openstack-ceilometer-collector restart

to install/update a new RPM after commiting changes to local repo: tito build --test --rpm --install; service openstack-ceilometer-collector restart

log messages are sent to /var/log/ceilometer/collector.log

TODO
----

 * nosetests
 * feed host/guest info to katello from ceilometer events
 * create system checkins from hourly instance.exists events
