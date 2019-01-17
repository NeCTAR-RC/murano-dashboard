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

from keystoneauth1.identity import v3
from keystoneauth1 import session

from openstack_dashboard.api import base


def get_auth_params_from_request(request):
    """Extracts properties needed by designateclient from the request object.

    These will be used to memoize the calls to designateclient.
    """
    return (
        request.user.token.id,
        request.user.tenant_id,
        request.user.token.project.get('domain_id'),
        base.url_for(request, 'dns'),
        base.url_for(request, 'identity')
    )


def designateclient(request_auth_params):
    (
        token,
        project_id,
        project_domain_id,
        designate_url,
        auth_url
    ) = request_auth_params

    auth = v3.Token(auth_url=auth_url,
                    token=token,
                    project_id=project_id,
                    project_domain_id=project_domain_id)
    sess = session.Session(auth=auth)
    d = designate_client.Client(session=sess)
    return d


def zone_list(request):
    d_client = designateclient(request)
    if d_client is None:
        return []
    return d_client.zones.list()
