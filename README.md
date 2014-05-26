![build status](https://api.travis-ci.org/Katello/katello_notification.png?branch=master)

katello_notification
====================

This is a daemon that reads data from the OpenStack message bus (either rabbit
or qpid) and feeds instance data directly into Katello. Currently, host/guest
UUID mappings are sent via katello_notification to either Katello or Spacewalk.

setup
-----

 * set up an openstack instance if one does not already exist. RDO works fine for this.
 * edit `/etc/katello/katello_notification.conf` to point to your katello or spacewalk instance.
 * start katello_notification (`systemctl start katello_notification`)
 * edit `/etc/nova/nova.conf`:
```
    -#notification_driver=
    +notification_driver=messaging

    -#notification_topics=notifications
    +notification_topics=notifications,subscription_notifications

    -#instance_usage_audit_period=month
    +instance_usage_audit_period=hour

    -#instance_usage_audit=false
    +instance_usage_audit=true
```

  * restart nova via `openstack-service restart nova`

troubleshooting
---------------

You should see messages in `/var/log/katello/katello_notification.log`. An
example successful startup looks like this:

    2014-05-19 17:36:13,240 - katello_notification - @katello_payload_actions.py INFO - initializing payload actions
    2014-05-19 17:36:13,241 - katello_notification - @katello_wrapper.py INFO - connecting to https://xxx.xxx.xxx.xxx:443/sam
    2014-05-19 17:36:13,241 - katello_notification - @katello_wrapper.py INFO - hypervisor autoregistration is disabled
    2014-05-19 17:36:13,312 - katello_notification - @notification.py INFO - listener initialized

When a system appears in OpenStack, nova generates an event. This event is read
by katello_notification which then fires a message to either Katello or
Spacewalk. You should see log messages appear when this happens. If not, then
ensure that nova.conf was set up correctly, and that nova was restarted _after_
katello_notification was started. In some cases, nova will not publish to the
subscription_notification topic unless katello_notification has already
registered as a reader.

Note also that katello_notification simply sends host/guest information in a
similar fashion to virt-who or rhn-virtualization-host; it does not register
guests. However, once guests register, they should be associated with the
correct hypervisor.

Hypervisors are _not_ registered by default. If the hypervisor is not capable
of registering istelf to Katello or Spacewalk, you may set
`autoregister_hypervisors = true` in katello_notification.conf


requirements
------------
 * an Icehouse-based OpenStack installation
 * either a Katello (pre-1.5) or Spacewalk instance


development howto
-----------------

 * fork a copy of https://github.com/Katello/katello_notification
 * write some failing nosetests, just run "make" to run them
 * fix tests
 * integration test (still manual process for now)
 * commit, push to your fork, create a PR
 * wait for travis to run
 * wait for an ACK + merge
 * done!
