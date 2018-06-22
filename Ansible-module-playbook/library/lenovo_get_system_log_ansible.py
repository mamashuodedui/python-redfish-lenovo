###
#
# Lenovo Redfish examples - Get the system_log information
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

# import lenovo_utils as utils

def get_system_url(base_url, redfish_obj):
    """Get ComputerSystem instance URL    
    :params base_url: URL of the Redfish Service Root
    :type base_url: string
    :params http_response: Response from HTTP
    :type redfish_obj: redfish client object
    :returns: returns string URL to ComputerSystem resource
    """
    # Get ServiceRoot resource
    response_base_url = redfish_obj.get(base_url, None)

    # Get ComputerSystemCollection resource
    systems_url = response_base_url.dict["Systems"]["@odata.id"]
    response_systems_url = redfish_obj.get(systems_url, None)

    # Get the first ComputerSystem resource from the collection members
    #  NOTE: Assume only 1 ComputerSystem instance
    system = []
    for i in range(response_systems_url.dict['Members@odata.count']):
        system_url = response_systems_url.dict["Members"][i]["@odata.id"]
        system.append(system_url)
    return system


def get_extended_error(response_body):
    expected_dict = response_body.dict
    message_dict = expected_dict["error"]["@Message.ExtendedInfo"][0]
    return str(message_dict["Message"])


def get_system_log(ip, login_account, login_password ):
    login_host = 'https://' + ip
    result = {}
    log_details = []
    login_host = 'https://' + ip
    # Connect using the address, account name, and password

    ## Create a REDFISH object
    REDFISH_OBJ = redfish.redfish_client(base_url=login_host, username=login_account,
                                         password=login_password, default_prefix='/redfish/v1')

    # Login into the server and create a session
    try:
        REDFISH_OBJ.login(auth="session")
    except:
        result = {'ret': False, 'msg': "Please check the username, password, IP is correct"}
        return result
    # GET the ComputerSystem resource
    system = get_system_url("/redfish/v1", REDFISH_OBJ)
    for i in range(len(system)):
        system_url = system[i]
        response_system_url = REDFISH_OBJ.get(system_url, None)
        if response_system_url.status == 200:
            # Get the ComputerProcessors resource
            LogServices_url = response_system_url.dict['LogServices']['@odata.id']
        else:
            result = {'ret': False, 'msg': "response system url Error code %s" % response_system_url.status}
            REDFISH_OBJ.logout()
            return result
        response_logservices_url = REDFISH_OBJ.get(LogServices_url, None)
        if response_logservices_url.status == 200:
            members = response_logservices_url.dict['Members']
        else:
            
            result = {'ret': False, 'msg': "response logservices url Error code %s" % response_logservices_url.status}
            REDFISH_OBJ.logout()
            return result

        for member in members:
            log_url = member['@odata.id']
            temp_list = log_url.split('/')
            log_name = temp_list[-2]
            response_log_url = REDFISH_OBJ.get(log_url, None)
            if response_log_url.status == 200:
                entries_url = response_log_url.dict['Entries']['@odata.id']
                response_entries_url = REDFISH_OBJ.get(entries_url, None)
                if response_entries_url.status == 200:
                    description = response_entries_url.dict['Description']
                    for logEntry in response_entries_url.dict['Members']:
                        entry = {}
                        # I only extract some fields
                        name = logEntry['Name']
                        created = logEntry['Created']
                        message = logEntry['Message']
                        severity = logEntry['Severity']

                        entry['Name'] = name
                        entry['Message'] = message
                        entry['Created'] = created
                        entry['Severity'] = severity
                        log_details.append(entry)
                else:
                    result = {'ret': False, 'msg': "response members url Error code %s" % response_entries_url.status}
                    REDFISH_OBJ.logout()
                    return result
                
            else:
                result = {'ret': False, 'msg': "response members url Error code %s" % response_log_url.status}
                REDFISH_OBJ.logout()
                return result
                
    result['ret'] = True            
    result['entries'] = log_details
    # Logout of the current session
    REDFISH_OBJ.logout()
    return result

from ansible.module_utils.basic import *

def main():
    module = AnsibleModule(         
        argument_spec = dict(             
            bmc_ip      = dict(required=True, type='str'),             
            bmc_user    = dict(required=True, type='str'),             
            bmc_pass    = dict(required=True, type='str')))
    
    bmc_ip = module.params['bmc_ip']     
    bmc_user = module.params['bmc_user']     
    bmc_pass = module.params['bmc_pass']
    result = get_system_log(bmc_ip, bmc_user, bmc_pass)
    if result['ret'] is True:
        del result['ret']
        module.exit_json(changed=False, result=result)
        # sys.stdout.write(json.dumps(result['entries'], sort_keys=True, indent=2))
    else:
        module.fail_json(changed=False, msg=result['msg'])
        # sys.stderr.write(result['msg'])


if __name__ == '__main__':
    main()
