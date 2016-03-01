#    Copyright (c) 2014 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sys
import weakref

import six

from murano.dsl import dsl_types
from murano.dsl import exceptions
from murano.dsl import typespec


class MuranoProperty(dsl_types.MuranoProperty, typespec.Spec):
    def __init__(self, declaring_type, property_name, declaration):
        super(MuranoProperty, self).__init__(declaration, declaring_type)
        self._property_name = property_name
        self._declaring_type = weakref.ref(declaring_type)

    def validate(self, *args, **kwargs):
        try:
            return super(MuranoProperty, self).validate(*args, **kwargs)
        except exceptions.ContractViolationException as e:
            msg = u'[{0}.{1}{2}] {3}'.format(
                self.declaring_type.name, self.name, e.path, six.text_type(e))
            six.reraise(exceptions.ContractViolationException,
                        msg, sys.exc_info()[2])

    @property
    def declaring_type(self):
        return self._declaring_type()

    @property
    def name(self):
        return self._property_name

    def __repr__(self):
        return 'MuranoProperty({type}::{name})'.format(
            type=self.declaring_type.name, name=self.name)
