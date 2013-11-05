ceilometer_katello_dispatcher
=============================

to set up an rdo instance in a vm:

 * find a fedora machine
 * if intel, run "rmmod kvm_intel; modprobe kvm_intel nested=y"
 * create a rhel or centos vm. 4GB mem and 2 CPU works ok.
 * on the VM: follow http://openstack.redhat.com/QuickStartLatest or http://openstack.redhat.com/Quickstart
 * on the VM: check out and install dispatcher code, and edit /etc/ceilometer/ceilometer.conf (possibly entry_points.txt)
 * from the horizon dashboard, fire up an instance. Cirros works fine for this.
 * you should see output in /var/log/ceilometer/katello.log
 

to install: python ./setup.py install; service openstack-ceilometer-collector restart

to check for clean startup: grep katello /var/log/ceilometer/collector.log

if /var/log/ceilometer/katello.log exists, that means the dispatcher loaded properly
