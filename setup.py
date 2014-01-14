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
    name="katello_notification",
    version='0.0.5',
    description='an oslo messagebus reader for interpreting events relevant to katello',
    author='Chris Duryee',
    author_email='cduryee@redhat.com',
    url='http://github.com/Katello/ceilometer_katello_dispatcher',
    license='GPLv2',

    test_suite = 'nose.collector',

    packages    = ["katello_notification"],
    package_dir = {"katello_notification" : "src/katello_notification" },

    entry_points = {"katello.notification": "instance = ceilometer.compute.notifications:Instance"},



    classifiers = [
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python'
    ],
)

