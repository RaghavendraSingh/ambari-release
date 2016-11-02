"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
from unittest import TestCase


class TestBasicAdvisor(TestCase):
  def setUp(self):
    import imp
    self.maxDiff = None
    self.testDirectory = os.path.dirname(os.path.abspath(__file__))
    stackAdvisorPath = os.path.abspath(os.path.join(self.testDirectory, '../../../main/resources/stacks/stack_advisor.py'))

    default_sa_classname = 'DefaultStackAdvisor'

    with open(stackAdvisorPath, 'rb') as fp:
      stack_advisor_impl = imp.load_module('stack_advisor', fp, stackAdvisorPath, ('.py', 'rb', imp.PY_SOURCE))

    clazz = getattr(stack_advisor_impl, default_sa_classname)
    self.stackAdvisor = clazz()

  def test_filterHostMounts(self):

    filtered_mount = "/data"

    hosts = {
      "items": [
        {
          "Hosts": {
            "cpu_count": 4,
            "total_mem": 50331648,
            "disk_info": [
              {"mountpoint": "/"},
              {"mountpoint": "/dev/shm"},
              {"mountpoint": "/vagrant"},
              {"mountpoint": "/dev/shm"},
              {"mountpoint": "/vagrant"},
              {"mountpoint": filtered_mount},
            ],
            "public_host_name": "c6401.ambari.apache.org",
            "host_name": "c6401.ambari.apache.org"
          },
        },
        {
          "Hosts": {
            "cpu_count": 4,
            "total_mem": 50331648,
            "disk_info": [
              {"mountpoint": "/"},
              {"mountpoint": "/dev/shm1"},
              {"mountpoint": "/vagrant1"},
              {"mountpoint": filtered_mount}
            ],
            "public_host_name": "c6402.ambari.apache.org",
            "host_name": "c6402.ambari.apache.org"
          },
        }
      ]
    }

    services = {
      "Versions": {
        "parent_stack_version": "2.5",
        "stack_name": "HDP",
        "stack_version": "2.6",
        "stack_hierarchy": {
          "stack_name": "HDP",
          "stack_versions": ["2.5", "2.4", "2.3", "2.2", "2.1", "2.0.6"]
        }
      },
      "services": [
      ],
      "configurations": {
        "cluster-env": {
          "properties": {
            "agent_mounts_ignore_list": filtered_mount
          }
        }
      }
    }

    filtered_hosts = self.stackAdvisor.filterHostMounts(hosts, services)

    for host in filtered_hosts["items"]:
      self.assertEquals(False, filtered_mount in host["Hosts"]["disk_info"])

  def test_getMountPathVariations(self):

    filtered_mount = "/data"

    hosts = {
      "items": [
        {
          "Hosts": {
            "cpu_count": 4,
            "total_mem": 50331648,
            "disk_info": [
              {"mountpoint": "/"},
              {"mountpoint": "/dev/shm"},
              {"mountpoint": "/vagrant"},
              {"mountpoint": "/dev/shm"},
              {"mountpoint": "/vagrant"},
              {"mountpoint": filtered_mount},
            ],
            "public_host_name": "c6401.ambari.apache.org",
            "host_name": "c6401.ambari.apache.org"
          },
        },
        {
          "Hosts": {
            "cpu_count": 4,
            "total_mem": 50331648,
            "disk_info": [
              {"mountpoint": "/"},
              {"mountpoint": "/dev/shm1"},
              {"mountpoint": "/vagrant1"},
              {"mountpoint": filtered_mount}
            ],
            "public_host_name": "c6402.ambari.apache.org",
            "host_name": "c6402.ambari.apache.org"
          },
        }
      ]
    }

    services = {
      "Versions": {
        "parent_stack_version": "2.5",
        "stack_name": "HDP",
        "stack_version": "2.6",
        "stack_hierarchy": {
          "stack_name": "HDP",
          "stack_versions": ["2.5", "2.4", "2.3", "2.2", "2.1", "2.0.6"]
        }
      },
      "services": [
      ],
      "configurations": {
        "cluster-env": {
          "properties": {
            "agent_mounts_ignore_list": filtered_mount
          }
        }
      }
    }

    hosts = self.stackAdvisor.filterHostMounts(hosts, services)
    avail_mounts = self.stackAdvisor.getMountPathVariations("/test/folder", "DATANODE", services, hosts)

    self.assertEquals(True, avail_mounts is not None)
    self.assertEquals(1, len(avail_mounts))
    self.assertEquals("/test/folder", avail_mounts[0])

  def test_updateMountProperties(self):
    hosts = {
      "items": [
        {
          "Hosts": {
            "cpu_count": 4,
            "total_mem": 50331648,
            "disk_info": [
              {"mountpoint": "/"},
              {"mountpoint": "/dev/shm"},
              {"mountpoint": "/vagrant"},
              {"mountpoint": "/dev/shm"},
              {"mountpoint": "/vagrant"},
              {"mountpoint": "/data"},
            ],
            "public_host_name": "c6401.ambari.apache.org",
            "host_name": "c6401.ambari.apache.org"
          },
        },
        {
          "Hosts": {
            "cpu_count": 4,
            "total_mem": 50331648,
            "disk_info": [
              {"mountpoint": "/"},
              {"mountpoint": "/me"},
              {"mountpoint": "/dev/shm1"},
              {"mountpoint": "/vagrant1"},
              {"mountpoint": "/data"}
            ],
            "public_host_name": "c6402.ambari.apache.org",
            "host_name": "c6402.ambari.apache.org"
          },
        }
      ]
    }

    services = {
      "Versions": {
        "parent_stack_version": "2.5",
        "stack_name": "HDP",
        "stack_version": "2.6",
        "stack_hierarchy": {
          "stack_name": "HDP",
          "stack_versions": ["2.5", "2.4", "2.3", "2.2", "2.1", "2.0.6"]
        }
      },
      "services": [
      ],
      "configurations": {
        "cluster-env": {
          "properties": {
            "agent_mounts_ignore_list": ""
          }
        },
        "some-site": {
          "path_prop": "/test"
        }
      }
    }

    pathProperties = [
      ("path_prop", "DATANODE", "/test", "multi"),
    ]

    configurations = {}

    self.stackAdvisor.updateMountProperties("some-site", pathProperties, configurations, services, hosts)

    self.assertEquals("/test,/data/test", configurations["some-site"]["properties"]["path_prop"])
