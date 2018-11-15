###
#
# Lenovo Redfish examples - updata user password
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

def update_user_password(ip, login_account, login_password, username, new_password):
    """update user password    
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :params system_id: ComputerSystem instance id(None: first instance, All: all instances)
    :type system_id: None or string
    :params username: Username to be modified by the user
    :type username: string
    :params new_password: New password to be modified by the user
    :type new_password: string
    :returns: returns update user password result when succeeded or error message when failed
    """
    result = {}
    try:
        # Connect using the BMC address, account name, and password
        # Create a REDFISH object
        login_host = "https://" + ip
        REDFISH_OBJ = redfish.redfish_client(base_url=login_host, username=login_account,
                                             password=login_password, default_prefix='/redfish/v1')
        # Login into the server and create a session
        REDFISH_OBJ.login(auth="session")
    except:
        result = {'ret': False, 'msg': "Please check the username, password, IP is correct\n"}
        return result
    try:
        # Get response_base_url resource
        response_base_url = REDFISH_OBJ.get('/redfish/v1', None)

        # Get account service url
        if response_base_url.status == 200:
            account_service_url = response_base_url.dict['AccountService']['@odata.id']
        else:
            error_message = utils.get_extended_error(response_base_url)
            result = {'ret': False, 'msg': "Url '/redfish/v1' response Error code %s \nerror_message: %s" % (
            response_base_url.status, error_message)}
            return result

        # Get AccountService resource
        response_account_service_url = REDFISH_OBJ.get(account_service_url, None)
        if response_account_service_url.status == 200:
            accounts_url = response_account_service_url.dict['Accounts']['@odata.id']
        else:
            error_message = utils.get_extended_error(response_account_service_url)
            result = {'ret': False, 'msg': "Url '%s' response Error code %s \nerror_message: %s" % (account_service_url, response_account_service_url.status, error_message)}
            return result

        # Get url accounts resource
        response_accounts_url = REDFISH_OBJ.get(accounts_url, None)
        if response_accounts_url.status == 200:
            account_count = response_accounts_url.dict["Members@odata.count"]
            # Loop the BMC user list and get all the bmc username
            for x in range(0, account_count):
                account_x_url = response_accounts_url.dict["Members"][x]["@odata.id"]
                response_account_x_url = REDFISH_OBJ.get(account_x_url, None)
                if response_account_x_url.status == 200:
                    bmc_username = response_account_x_url.dict['UserName']
                    # Update the BMC user password when the specified BMC username is in the BMC user list.
                    if bmc_username == username:
                        if "@odata.etag" in response_account_x_url.dict:
                            etag = response_account_x_url.dict['@odata.etag']
                        else:
                            etag = ""
                        headers = {"If-Match": etag}
                        parameter = {"Password": new_password}
                        response_modified_password = REDFISH_OBJ.patch(account_x_url, body=parameter, headers=headers)
                        if response_modified_password.status == 200:
                            result = {'ret': True, 'msg': "The BMC user '%s' password is successfully updated." % username}
                            return result
                        else:
                            error_message = utils.get_extended_error(response_modified_password)
                            result = {'ret': False, 'msg': "Update BMC user password failed, url '%s' response error code %s \nerror_message: %s" % (account_x_url, response_modified_password.status, error_message)}
                            return result

                # account_x_url response failed
                else:
                    try:
                        error_message = utils.get_extended_error(response_account_x_url)
                    except:
                        error_message = response_account_x_url
                    result = {'ret': False, 'msg': "response_account_x_url Error code %s \nerror_message: %s" % (
                        response_account_x_url.status, error_message)}
                    return result
            result = {'ret': False, 'msg': "Specified BMC username doesn't exist. Please check whether the BMC username is correct."}
        else:
            error_message = utils.get_extended_error(response_accounts_url)
            result = {'ret': False, 'msg': "Url '%s' response error code %s \nerror_message: %s" % (accounts_url,
            response_accounts_url.status, error_message)}
    except Exception as e:
        result = {'ret':False, 'msg':"Error message %s" %e}
    finally:
        # Logout of the current session
        REDFISH_OBJ.logout()
        return result


import argparse
def add_parameter():
    """Add update user password parameter"""
    argget = utils.create_common_parameter_list()
    argget.add_argument('--username', type=str, help='Input the update BMC user name')
    argget.add_argument('--newpasswd', type=str, help='Input the BMC user new password')
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)
    if args.username is not None and args.newpasswd is not None:
        parameter_info["username"] = args.username
        parameter_info["new_passwd"] = args.newpasswd
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
        username = parameter_info['username']
        new_password = parameter_info['new_passwd']
    except:
        sys.stderr.write("Please run the command 'python %s -h' to view the help info" % sys.argv[0])
        sys.exit(1)

    # Update user password result and check result   
    result = update_user_password(ip, login_account, login_password, username, new_password)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])