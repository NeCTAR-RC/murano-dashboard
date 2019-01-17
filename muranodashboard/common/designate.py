# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from designateclient.v2 import client as designate_client
from django.conf import settings

from horizon.utils.memoized import memoized_with_request

from keystoneauth1 import loading  
from keystoneauth1 import session

from openstack_dashboard.api import base
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


def get_auth_params_from_request(request):
    """Extracts properties needed by designateclient from the request object.

    These will be used to memoize the calls to designateclient.
    """
    return (
        request.user.token.id,
        base.url_for(request, 'dns'),
        base.url_for(request, 'identity')
    )

@memoized_with_request(get_auth_params_from_request)
def designateclient(request_auth_params):
    (
        token_id,
        designate_url,
        auth_url
    ) = request_auth_params

    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)

    loader = loading.get_plugin_loader('token')
    auth = loader.load_from_options(auth_url=auth_url, token=token_id)
    sess = session.Session(auth=auth)
    d = designate_client.Client(session=sess)
    return d

def zone_get(request, zone_id):
    d_client = designateclient(request)
    if d_client is None:
        return []
    return d_client.zones.get(zone_id)


def zone_list(request):
    d_client = designateclient(request)
    if d_client is None:
        return []
    return d_client.zones.list()


def zone_create(request, name, email, ttl=None, description=None):
    d_client = designateclient(request)
    if d_client is None:
        return None

    options = {
        'description': description,
    }

    # TTL needs to be optionally added as argument because the client
    # won't accept a None value
    if ttl is not None:
        options['ttl'] = ttl

    return d_client.zones.create(name=name, email=email, **options)


def zone_update(request, zone_id, email, ttl, description=None):
    d_client = designateclient(request)
    if d_client is None:
        return None

    return d_client.zones.update(zone_id, zone_id, email, ttl, description=None)


def zone_delete(request, zone_id):
    d_client = designateclient(request)
    if d_client is None:
        return []
    return d_client.zones.delete(zone_id)


def recordset_list(request, zone_id):
    d_client = designateclient(request)
    if d_client is None:
        return []
    return d_client.recordsets.list(zone_id)


def recordset_get(request, zone_id, recordset_id):
    d_client = designateclient(request)
    if d_client is None:
        return []
    return d_client.recordsets.get(zone_id, recordset_id)


def recordset_delete(request, zone_id, recordset_id):
    d_client = designateclient(request)
    if d_client is None:
        return []
    return d_client.recordsets.delete(zone_id, recordset_id)


def recordset_create(request, zone_id, **kwargs):
    d_client = designateclient(request)
    if d_client is None:
        return []

    return d_client.recordsets.create(zone_id, **kwargs)


def recordset_update(request, zone_id, recordset_id, **kwargs):
    d_client = designateclient(request)
    if d_client is None:
        return []

    # TODO(andybotting) Update this
    return d_client.recordsets.update(zone_id, **kwargs)
