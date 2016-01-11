# Copyright (c) 2015 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import json

import cfg
import glanceclient
from oslo_config import cfg as config
from oslo_log import log as logging


import murano.dsl.helpers as helpers


CONF = config.CONF
LOG = logging.getLogger(__name__)


class GlanceClient(object):
    def __init__(self, context):
        client_manager = helpers.get_environment(context).clients
        self.client = client_manager.get_client("glance", True,
                                                self.create_glance_client)

    def list(self):
        images = self.client.images.list()
        while True:
            try:
                image = images.next()
                yield GlanceClient._format(image)
            except StopIteration:
                break

    def get_by_name(self, name):
        images = list(self.client.images.list(filters={"name": name}))
        if len(images) > 1:
            raise AmbiguousNameException(name)
        elif len(images) == 0:
            return None
        else:
            return GlanceClient._format(images[0])

    def get_by_id(self, imageId):
        image = self.client.images.get(imageId)
        return GlanceClient._format(image)

    @staticmethod
    def _format(image):
        res = {"id": image.id, "name": image.name}
        if hasattr(image, "murano_image_info"):
            res["meta"] = json.loads(image.murano_image_info)
        return res

    @classmethod
    def init_plugin(cls):
        cls.CONF = cfg.init_config(CONF)

    def create_glance_client(self, keystone_client, auth_token):
        LOG.debug("Creating a glance client")
        glance_endpoint = keystone_client.service_catalog.url_for(
            service_type='image', endpoint_type=self.CONF.endpoint_type)
        client = glanceclient.Client(self.CONF.api_version,
                                     endpoint=glance_endpoint,
                                     token=auth_token)
        return client


class AmbiguousNameException(Exception):
    def __init__(self, name):
        super(AmbiguousNameException, self).__init__("Image name '%s'"
                                                     " is ambiguous" % name)
