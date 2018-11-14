###
#
# Lenovo Redfish examples - Delete bmc user
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


def delete_bmc_user(ip, login_account, login_password, username):
    """Delete bmc user
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :params username:BMC user name by user specified
    :type username: string
    :returns: returns disable user result when succeeded or error message when failed
    """
    result = {}
    if username == "" or username.strip() == "":
        result = {"ret":False,"msg":"username invalid please check your input"}
        return result
    login_host = "https://" + ip
    try:
        # Connect using the BMC address, account name, and password
        # Create a REDFISH object
        REDFISH_OBJ = redfish.redfish_client(base_url=login_host, username=login_account,
                                             password=login_password, default_prefix='/redfish/v1')
        # Login into the server and create a session
        REDFISH_OBJ.login(auth="session")
    except:
        result = {'ret': False, 'msg': "Please check the username, password, IP is correct\n"}
        return result
    # Get ServiceRoot resource
    response_base_url = REDFISH_OBJ.get('/redfish/v1', None)

    # Get response_account_service_url
    if response_base_url.status == 200:
        account_service_url = response_base_url.dict['AccountService']['@odata.id']
    else:
        REDFISH_OBJ.logout()
        result = {'ret': False, 'msg': "response base url Error code %s" % response_base_url.status}
        return result
    # Get AccountService resource
    response_account_service_url = REDFISH_OBJ.get(account_service_url, None)
    if response_account_service_url.status == 200:
        accounts_url = response_account_service_url.dict['Accounts']['@odata.id']
        response_accounts_url = REDFISH_OBJ.get(accounts_url, None)
        # Get the user account url
        if response_accounts_url.status == 200:
            max_account_num = response_accounts_url.dict["Members@odata.count"]
            list_account_url = []
            for i in range(max_account_num):
                account_url = response_accounts_url.dict["Members"][i]["@odata.id"]
                list_account_url.append(account_url)
            dest_account_url = ""
            for account_url in list_account_url:
                response_account_url = REDFISH_OBJ.get(account_url, None)
                if response_account_url.status == 200:
                    account_username = response_account_url.dict["UserName"]
                    if account_username == username:
                        dest_account_url = account_url
                        break
                else:
                    REDFISH_OBJ.logout()
                    result = {'ret': False,
                              'msg': "response accounts url Error code %s" % response_account_url.status}
                    return result
            if dest_account_url == "":
                REDFISH_OBJ.logout()
                result = {'ret': False,
                          'msg': "Account %s is not existed" %username}
                return result
            if "@odata.etag" in response_account_url.dict:
                etag = response_account_url.dict['@odata.etag']
            else:
                etag = ""
            headers = {"If-Match": etag, }
            # Set the body info
            parameter = {
                "UserName": ""
            }
            #delete bmc user
            response_delete_account_url = REDFISH_OBJ.patch(dest_account_url, body=parameter, headers=headers)
            if response_delete_account_url.status == 200:
                result = {'ret': True, 'msg': "account %s delete successfully" % username}
                REDFISH_OBJ.logout()
                return result
            else:
                result = {'ret': False, 'msg': "response delete account url Error code %s" % response_delete_account_url.status}
                REDFISH_OBJ.logout()
                return result
        else:
            REDFISH_OBJ.logout()
            result = {'ret': False,
                      'msg': "response accounts url Error code %s" % response_accounts_url.status}
            return result
    else:
        REDFISH_OBJ.logout()
        result = {'ret': False,
                  'msg': "response account service url Error code %s" % response_account_service_url.status}
        return result


import argparse

def add_parameter():
    """Add delete bmc user parameter"""
    parameter_info = {}
    argget = utils.create_common_parameter_list()
    argget.add_argument('--username', type=str, help='Input the username')
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)
    parameter_info["username"] = args.username
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
    except:
        sys.stderr.write("Please run the coommand 'python %s -h' to view the help info" % sys.argv[0])
        sys.exit(1)

    # Get delete bmc user result and check result
    result = delete_bmc_user(ip, login_account, login_password,username)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])