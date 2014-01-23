#!/usr/bin/python
import simplejson
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class ConsumerMap():
    """
    this is a wrapper for looking up consumer UUIDs for systems
    """

    def _load_consumer_map(self, fname):
        """
        broken out just to make mocking easier
        """
        read_data = {}
        try:
            with open(fname, 'r') as f:
                try:
                    read_data = simplejson.load(f)
                except ValueError:
                    log.error("json file  %s is corrupt or empty, data will be reset on next write" % fname)
        except IOError:
            log.error("unable to open %s, no hypervisor map will be loaded" % fname)

        return read_data

    def _save_consumer_map(self, fname, data, debug=True):
        """
        broken out to make mocking easier
        """
        log.debug("attempting to write data: %s" % data)
        try:
            with open(fname, "w+") as f:
                simplejson.dump(data, f)
            if debug:
                log.debug("Wrote mapping to %s" % fname)
        except IOError, e:
            if debug:
                log.error("Unable to write mapping to %s" % fname)
                log.exception(e)

    def __init__(self, hyp_json_filename):
        """
        load map, etc
        """
        self.hypervisor_consumer_json_fname = hyp_json_filename
        self.hypervisor_consumer_map = self._load_consumer_map(hyp_json_filename)

    def find_hypervisor_consumer_uuid(self, local_identifier):
        """
        given a hypervisor's local identifier (ex: hostname), find its consumer uuid

        raises a KeyError when a value is not found
        """
        return self.hypervisor_consumer_map[local_identifier]

    def add_hypervisor_consumer_uuid(self, local_identifier, hyp_uuid):
        """
        save hypervisor uuid to map
        """
        self.hypervisor_consumer_map[local_identifier] = hyp_uuid
        # save immediately
        self._save_consumer_map(fname=self.hypervisor_consumer_json_fname, data=self.hypervisor_consumer_map)

    def remove_hypervisor_consumer_uuid(self, local_identifier):
        """
        remove hypervisor uuid from map
        """
        del self.hypervisor_consumer_map[local_identifier]
        # save immediately
        self._save_consumer_map(fname=self.hypervisor_consumer_json_fname, data=self.hypervisor_consumer_map)
