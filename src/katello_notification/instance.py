#based on ceilometer.compute.notification.instance

from ceilometer.compute import notifications
from ceilometer import sample

class Instance(notifications.ComputeNotificationBase):
    event_types = ['compute.instance.create.end', 'compute.instance.exists']

    def process_notification(self, message):
        yield sample.Sample.from_notification(
            name='instance',
            type=sample.TYPE_GAUGE,
            unit='instance',
            volume=1,
            user_id=message['payload']['user_id'],
            project_id=message['payload']['tenant_id'],
            resource_id=message['payload']['instance_id'],
            message=message)
