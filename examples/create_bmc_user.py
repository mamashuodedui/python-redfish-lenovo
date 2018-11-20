###
#
# Lenovo Redfish examples - Create bmc user
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

#set user privileges
def set_user_privileges(REDFISH_OBJ,response_account_service_url,roleid,authority):
    result = {}
    list_auth = []
    #check custom privileges
    rang_custom_auth = ("UserAccountManagement","RemoteConsoleAccess","RemoteConsoleAndVirtualMediaAcccess","RemoteServerPowerRestartAccess","AbilityClearEventLogs","AdapterConfiguration_Basic"
,"AdapterConfiguration_NetworkingAndSecurity","AdapterConfiguration_Advanced")
    for auth in authority:
        if auth not in rang_custom_auth:
            result = {'ret': False, 'msg': "custom privileges out of rang"}
            return result
        list_auth.append(auth)
    roles_url = response_account_service_url.dict['Roles']['@odata.id']
    response_roles_url = REDFISH_OBJ.get(roles_url, None)
    if response_roles_url.status == 200:
        max_role_num = response_roles_url.dict["Members@odata.count"]
        list_role_url = []
        for i in range(max_role_num):
            role_url = response_roles_url.dict["Members"][i]["@odata.id"]
            list_role_url.append(role_url)
        dst_role_url = ""
        for role_url in list_role_url:
            response_role_url = REDFISH_OBJ.get(role_url, None)
            if response_role_url.status == 200:
                role_username = response_role_url.dict["Name"]
                if role_username == roleid:
                    dst_role_url = role_url
                    break
            else:
                result = {'ret': False, 'msg': "response roles url Error code %s" % response_roles_url.status}
                return result
        if dst_role_url == "":
            result = {'ret': False, 'msg': "roles is not existed"}
            REDFISH_OBJ.logout()
            return result
        response_role_url = REDFISH_OBJ.get(dst_role_url, None)
        if response_role_url.status != 200:
            result = {'ret': False, 'msg': "response role url Error code %s" % response_role_url.status}
            REDFISH_OBJ.logout()
            return result
        parameter = {
            "OemPrivileges": list_auth
        }
        response_update_role_url = REDFISH_OBJ.patch(dst_role_url, body=parameter)
        if response_update_role_url.status == 200:
            result = {'ret': True, 'msg': "update role auth successful"}
            return result
        else:
            try:
                error_message = utils.get_extended_error(response_update_role_url)
            except:
                error_message = response_update_role_url
            result = {'ret': False, 'msg': "response update role url Error code %s\n msg is %s" % (
            response_update_role_url.status, error_message)}
            return result
    else:
        result = {'ret': False,
                  'msg': "response roles url Error code %s" % response_roles_url.status}
        return result



def create_bmc_user(ip, login_account, login_password, username, password,authority):
    """create bmc user
    :params ip: BMC IP address
    :type ip: string
    :params login_account: BMC user name
    :type login_account: string
    :params login_password: BMC user password
    :type login_password: string
    :params username: new  username by user specified
    :type userid: string
    :params password: new password by user specified
    :type password: string
    :params authority: user authority by user specified
    :type authority: list
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

    # Get ServiceBase resource
    response_base_url = REDFISH_OBJ.get('/redfish/v1', None)
    # Get response_base_url
    if response_base_url.status == 200:
        account_service_url = response_base_url.dict['AccountService']['@odata.id']
    else:
        result = {'ret': False, 'msg': " response base url Error code %s" % response_base_url.status}
        REDFISH_OBJ.logout()
        return result
    response_account_service_url = REDFISH_OBJ.get(account_service_url, None)
    if response_account_service_url.status == 200:
        accounts_url = response_account_service_url.dict['Accounts']['@odata.id']
        response_accounts_url = REDFISH_OBJ.get(accounts_url, None)
        if response_accounts_url.status == 200:
            max_account_num = response_accounts_url.dict["Members@odata.count"]
            list_account_url = []
            for i in range(max_account_num):
                account_url = response_accounts_url.dict["Members"][i]["@odata.id"]
                list_account_url.append(account_url)
            first_empty_account = ""
            flag = False
            user_pos = 0
            num = 0
            #find the first empty account pos
            for account_url in list_account_url:
                num = num + 1
                response_accounts_url = REDFISH_OBJ.get(account_url, None)
                if response_accounts_url.status == 200:
                    account_username = response_accounts_url.dict["UserName"]
                    if account_username == "" and flag is False:
                        first_empty_account = account_url
                        flag = True
                        user_pos = num
                    elif account_username == username:
                        result = {'ret': False, 'msg': "username %s is existed" %username}
                        REDFISH_OBJ.logout()
                        return result
                else:
                    result = {'ret': False, 'msg': "response accounts url Error code %s" % response_accounts_url.status}
                    REDFISH_OBJ.logout()
                    return result
            if first_empty_account == "":
                result = {'ret': False, 'msg': "accounts is full,can't create a new account"}
                REDFISH_OBJ.logout()
                return result

            #set user privilege
            rolename = ""
            if len(authority) == 1 and authority[0] == "Supervisor":
                rolename = "Administrator"
            elif len(authority) == 1 and  authority[0] == "ReadOnly":
                rolename = "ReadOnly"
            else:
                rolename = "CustomRole" + str(user_pos)
                result = set_user_privileges(REDFISH_OBJ,response_account_service_url,rolename,authority)
                if result['ret'] == False:
                    REDFISH_OBJ.logout()
                    return result
            if rolename == "":
                result = {'ret': False,
                          'msg': "authority error"}
                REDFISH_OBJ.logout()
                return result
            else:
                sys.stdout.write(rolename + '\n')


            #create new user account
            response_empty_account_url = REDFISH_OBJ.get(first_empty_account, None)
            if response_empty_account_url.status != 200:
                result = {'ret': False, 'msg': "response_empty_account_url Error code %s" % response_empty_account_url.status}
                REDFISH_OBJ.logout()
                return result
            if "@odata.etag" in response_empty_account_url.dict:
                etag = response_empty_account_url.dict['@odata.etag']
            else:
                etag = ""
            headers = {"If-Match": etag}
            parameter = {
                "Password": password,
                "UserName": username,
                "RoleId":rolename
                }
            response_create_url = REDFISH_OBJ.patch(first_empty_account, body=parameter, headers=headers)
            if response_create_url.status == 200:
                result = {'ret': True, 'msg': "create new user successful"}
                REDFISH_OBJ.logout()
                return result
            else:
                try:
                    error_message = utils.get_extended_error(response_create_url)
                except:
                    error_message = response_create_url
                result = {'ret': False, 'msg': "response account url Error code %s\n msg is %s" % (response_create_url.status,error_message)}
                REDFISH_OBJ.logout()
                return result
        else:
            result = {'ret': False,
                      'msg': "response accounts  url Error code %s" % response_accounts_url.status}
            REDFISH_OBJ.logout()
            return result
    else:
        result = {'ret': False, 'msg': "response account service url Error code %s" % response_account_service_url.status}
        REDFISH_OBJ.logout()
        return result

    REDFISH_OBJ.logout()
    return result


import argparse

def add_parameter():
    """Add create bmc user parameter"""
    parameter_info = {}
    argget = utils.create_common_parameter_list()
    argget.add_argument('--newusername', type=str, help='Input the update account username')
    argget.add_argument('--newuserpasswd', type=str, help='Input the user new userpasswd')
    help_str = "The value of this parameter shall be the privileges that this user includes."
    help_str += "For super user, this property shall be Supervisor. default is super user. "
    help_str += "For pre-defined user, this property shall be ReadOnly. "
    help_str += "For custom user some implementations may not allow writing this property."
    help_str += "You can only choose one or more values in the list:[UserroleManagement,RemoteConsoleAccess,RemoteConsoleAndVirtualMediaAcccess,RemoteServerPowerRestartAccess,"
    help_str += "AbilityClearEventLogs,AdapterConfiguration_Basic,AdapterConfiguration_NetworkingAndSecurity,AdapterConfiguration_Advanced]"
    argget.add_argument('--authority', nargs='*', default=["Supervisor"], help=help_str)

    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)
    parameter_info["newusername"] = args.newusername
    parameter_info["newuserpasswd"] = args.newuserpasswd
    parameter_info["authority"] = args.authority
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
        username = parameter_info['newusername']
        password = parameter_info['newuserpasswd']
        authority = parameter_info['authority']
    except:
        sys.stderr.write("Please run the command 'python %s -h' to view the help info" % sys.argv[0])
        sys.exit(1)

    # create bmc user result and check result
    result = create_bmc_user(ip, login_account, login_password, username, password,authority)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])