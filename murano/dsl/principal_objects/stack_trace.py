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

import inspect
import os.path

from murano.dsl import helpers
from murano.dsl import murano_class
from murano.dsl import murano_object
from murano.dsl import yaql_expression


@murano_class.classname('io.murano.StackTrace')
class StackTrace(murano_object.MuranoObject):
    def initialize(self, _context, includeNativeFrames=True):
        frames = []
        context = _context
        while True:
            if not context:
                break
            instruction = helpers.get_current_instruction(context)
            frames.append({
                'instruction': None if instruction is None
                else str(instruction),

                'location': None if instruction is None
                else instruction.source_file_position,

                'method': helpers.get_current_method(context),
                'class': helpers.get_type(context)
            })
            context = helpers.get_caller_context(context)
        frames.pop()
        frames.reverse()

        if includeNativeFrames:
            class InstructionStub(object):
                def __init__(self, title, position):
                    self._title = title
                    self.source_file_position = position

                def __str__(self):
                    return self._title

            native_frames = []
            for frame in inspect.trace()[1:]:
                info = inspect.getframeinfo(frame[0])
                position = yaql_expression.YaqlExpressionFilePosition(
                    os.path.abspath(info.filename), info.lineno,
                    -1, -1, -1, -1, -1)
                instruction = InstructionStub(
                    info.code_context[0].strip(), position)
                method = info.function
                native_frames.append({
                    'instruction': instruction,
                    'method': method,
                    'class': None
                })
            frames.extend(native_frames)

        self.set_property('frames', frames)

    def toString(self, prefix=''):
        def format_frame(frame):
            instruction = frame['instruction']
            method = frame['method']
            murano_class = frame['class']
            location = frame['location']

            if location:
                args = (
                    os.path.abspath(location.file_path),
                    location.start_line,
                    ':' + str(location.start_column)
                    if location.start_column >= 0 else '',
                    method,
                    instruction,
                    prefix,
                    '' if not murano_class else murano_class.name + '::'
                )
                return '{5}File "{0}", line {1}{2} in method {6}{3}\n' \
                       '{5}    {4}'.format(*args)
            else:
                return '{2}File <unknown> in method {3}{0}\n{2}    {1}'.format(
                    method, instruction, prefix,
                    '' if not murano_class else murano_class.name + '::')

        return '\n'.join([format_frame(t)for t in self.get_property('frames')])
