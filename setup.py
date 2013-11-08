#!/usr/bin/env python
#
# Copyright (c) 2013 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.

from setuptools import setup, find_packages, Extension

setup(
    name="ceilometer_katello_dispatcher",
    version='0.0.4',
    description='A ceilometer dispatcher for feeding instance events into katello',
    author='Chris Duryee',
    author_email='cduryee@redhat.com',
    url='http://github.com/Katello/ceilometer_katello_dispatcher',
    license='GPLv2',

    test_suite = 'nose.collector',

    packages    = ["ceilometer_katello_dispatcher"],
    package_dir = {"ceilometer_katello_dispatcher" : "src/ceilometer_katello_dispatcher" },

    entry_points = {"ceilometer.dispatcher": "katello = ceilometer_katello_dispatcher.katello_dispatcher:KatelloDispatcher"},


    classifiers = [
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python'
    ],
)

