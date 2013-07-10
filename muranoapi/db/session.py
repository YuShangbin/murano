# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Piston Cloud Computing, Inc.
# All Rights Reserved.
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
"""Session management functions."""

import os

from migrate.versioning import api as versioning_api
from migrate import exceptions as versioning_exceptions

from muranoapi.openstack.common.db.sqlalchemy import session
from muranoapi.common.config import CONF as conf
from muranoapi.openstack.common import log as logging
from muranoapi.db import migrate_repo

log = logging.getLogger(__name__)


def get_session(autocommit=True, expire_on_commit=False):
    if not session._MAKER:
        if conf.database.auto_create:
            log.info(_('auto-creating DB'))
            _auto_create_db()
        else:
            log.info(_('not auto-creating DB'))
    return session.get_session(autocommit, expire_on_commit)


def _auto_create_db():
    repo_path = os.path.abspath(os.path.dirname(migrate_repo.__file__))
    try:
        versioning_api.upgrade(conf.database.connection, repo_path)
    except versioning_exceptions.DatabaseNotControlledError:
        versioning_api.version_control(conf.database.connection, repo_path)
        versioning_api.upgrade(conf.database.connection, repo_path)