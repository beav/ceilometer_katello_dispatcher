ceilometer_katello_dispatcher
=============================

to set up an rdo instance in a vm:

 * find a fedora machine
 * if intel, run "rmmod kvm_intel; modprobe kvm_intel nested=y"
 * create a rhel or centos vm. 4GB mem and 2 CPU works ok.
 * on the VM: follow http://openstack.redhat.com/QuickStartLatest or http://openstack.redhat.com/Quickstart
 * on the VM: check out and install dispatcher code, and edit /etc/ceilometer/ceilometer.conf

        [dispatcher_katello]
        log_file_path = /var/log/ceilometer/katello.log
        default_owner = ACME_Corporation

        [collector]
        dispatchers = katello 
        dispatchers = database # this needs to be defined if we are also defining the katello dispatcher

 * on the VM: edit /usr/lib/python2.6/site-packages/ceilometer-2013.2-py2.6.egg-info/entry_points.txt (this step will go away)

        katello = ceilometer_katello_dispatcher.katello:KatelloDispatcher

 * on the VM: service openstack-ceilometer-collector restart
 * from the horizon dashboard, fire up an instance. Cirros works fine for this.
 * you should see output in /var/log/ceilometer/katello.log
 

to install: python ./setup.py install; service openstack-ceilometer-collector restart

to check for clean startup: grep katello /var/log/ceilometer/collector.log

if /var/log/ceilometer/katello.log exists, that means the dispatcher loaded properly
