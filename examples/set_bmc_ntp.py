###
#
# Lenovo Redfish examples - Set manager ntp
#
# Copyright Notice:
#
# Copyright 2018 Lenovo Corporation
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
###


import sys
import redfish
import json
import lenovo_utils as utils


def set_manager_ntp(ip, login_account, login_password, ntp_server, ProtocolEnabled):
    """Set manager ntp server
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :params ntp_server: ntp_server by user specified
    :type ntp_server: list
    :params ProtocolEnabled: ProtocolEnabled by user specified
    :type ProtocolEnabled: string
    :returns: returns set manager ntp result when succeeded or error message when failed
    """
    result = {}
    login_host = "https://" + ip

    # Connect using the BMC address, account name, and password
    # Create a REDFISH object
    REDFISH_OBJ = redfish.redfish_client(base_url=login_host, username=login_account,
                                         password=login_password, default_prefix='/redfish/v1')

    # Login into the server and create a session
    try:
        REDFISH_OBJ.login(auth="session")
    except:
        result = {'ret': False, 'msg': "Please check the username, password, IP is correct\n"}
        return result
    try:
        # Get ServiceBase resource
        response_base_url = REDFISH_OBJ.get('/redfish/v1', None)
        # Get response_base_url
        if response_base_url.status == 200:
            manager_url = response_base_url.dict['Managers']['@odata.id']
        else:
            error_message = utils.get_extended_error(response_base_url)
            result = {'ret': False, 'msg': "Url '/redfish/v1' response error code %s \nerror_message: %s" % (
                response_base_url.status, error_message)}
            return result
        response_manager_url = REDFISH_OBJ.get(manager_url, None)
        if response_manager_url.status == 200:
            for request in response_manager_url.dict['Members']:
                request_url = request['@odata.id']
                response_url = REDFISH_OBJ.get(request_url, None)
                if response_url.status == 200:
                    network_url = response_url.dict['NetworkProtocol']['@odata.id']
                    Protocol = {"NTPServers":ntp_server,"ProtocolEnabled":  bool(int(ProtocolEnabled))}
                    parameter = {"NTP": Protocol}
                    response_network_url = REDFISH_OBJ.patch(network_url, body=parameter)
                    if response_network_url.status == 200:
                        result = {'ret': True, 'msg': " Set manager ntp servers successfully"}
                    else:
                        error_message = utils.get_extended_error(response_network_url)
                        result = {'ret': False, 'msg': "Url '%s' response error code %s \nerror_message: %s" % (
                            network_url, response_network_url.status, error_message)}
                        return result
                else:
                    error_message = utils.get_extended_error(response_url)
                    result = {'ret': False, 'msg': "Url '%s' response error code %s \nerror_message: %s" % (
                        request_url, response_url.status, error_message)}
                    return result

        else:
            error_message = utils.get_extended_error(response_manager_url)
            result = {'ret': False, 'msg': "Url '%s' response error code %s \nerror_message: %s" % (
                manager_url, rresponse_manager_url.status, error_message)}
            return result
    except Exception as e:
        result = {'ret': False, 'msg': "error message %s" % e}
    finally:
        # Logout of the current session
        REDFISH_OBJ.logout()
        return result


import argparse
def add_parameter():
    """Add set manager ntp parameter"""
    argget = utils.create_common_parameter_list()
    argget.add_argument('--ntpserver', nargs=4, type=str, help='Input the ntp server(array  Items: string,Item count: 4)')
    argget.add_argument('--protocol', type=str, choices = ["0", "1"], help='Input the rotocolEnabled (0:false, 1:true)')
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)
    return parameter_info

if __name__ == '__main__':
    # Get parameters from config.ini and/or command line
    parameter_info = add_parameter()

    # Get connection info from the parameters user specified
    ip = parameter_info['ip']
    login_account = parameter_info["user"]
    login_password = parameter_info["passwd"]

    # Get set info from the parameters user specified
    try:
        ntp_server = parameter_info['ntp_server']
        ProtocolEnabled = parameter_info['ProtocolEnabled']
    except:
        sys.stderr.write("Please run the command 'python %s -h' to view the help info" % sys.argv[0])
        sys.exit(1)

    # Set manager ntp result and check result
    result = set_manager_ntp(ip, login_account, login_password, ntp_server, ProtocolEnabled)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])