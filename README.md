# Ansible module of Lenovo Open Source Python Scripts with Redfish APIs

Ansible module and playbooks that use the Redfish API to manage Lenovo ThinkSystem servers. 

## Why Ansible

Ansible is an open source automation engine that automates complex IT tasks such as cloud provisioning, application deployment and other maintenance tasks. It is a one-to-many agentless mechanism where complicated deployment tasks can be controlled and monitored from a central control machine.

To learn more about Ansible, click [here](http://docs.ansible.com/).

## Why Redfish

Redfish is an open industry-standard specification and schema designed for modern and secure management of platform hardware. On PowerEdge servers the Redfish management APIs are available via the BMC, which can be used by IT administrators to easily monitor and manage at scale their entire infrastructure using a wide array of clients on devices such as laptops, tablets and smart phones. 

To learn more about Redfish, click [here](https://www.dmtf.org/standards/redfish).

## Ansible and Redfish together

Together, Ansible and Redfish can be used by system administrators to fully automate at large scale server monitoring, alerting, configuration and firmware update tasks from one central location, significantly reducing complexity and helping improve the productivity and efficiency of IT administrators.

## Install Requirements
1. Install Redfish library from github
   Download Readfish library source code from https://github.com/DMTF/python-redfish-library, and then: 
   python setup.py install
2. Install Ansible:
   sudo apt install ansible
   sudo yum install ansible
3. If you are running selinux on client, you may need libselinux-python to support saving logfile on client, or you may disable selinux instead.
   To install libselinux-python: 
       sudo apt install libselinux-python
       sudo yum install libselinux-python


## How it works

Client communicates wtih BMC throught BMC IP address, sending Readfish URIs, then BMC will either return data in json format according to the URIs received, or perform specifc actions.


The file located in  */etc/ansible/hosts* should look like this:

```
[myhosts]
# Hostname        BMC IP(required)      BMC Credentials
hostname1.com     bmcip=192.168.0.101   bmc_user=root bmc_pass='*****'
hostname2.com     bmcip=192.168.0.102   bmc_user=root bmc_pass='*****'
hostname3.com     bmcip=192.168.0.103   bmc_user=root bmc_pass='*****'
...
```

Please note that BMC IP is required for coummunication between client and BMC. And if bmc_user and bmc_pass are not specified, defalut value will be applied which defined in 'group_vars/all' file.


## Example

In order to keep scripts working properly, please put all ansible modules in 'library' folder.

```bash
$ ansible-playbook lenovo_get_system_log.yml
  ...
PLAY [Get System Log] **********************************

TASK [Set timestamp ] **********************************************************
ok: [hostname1]
ok: [hostname2]
ok: [hostname3]
  --- snip ---
```

You will see the usual task execution output, but please note that all server information retrieved is collected and put into json files defined by the *rootdir* variable in the playbook. you may change it in 'group_var/all' file if necessary. The playbook creates a directory per server and places files there. For example:

```bash
$ cd <rootdir>/bmc_ip
$ ls
bmc_ip_SystemLog_20180620_055337.json
bmc_ip_SystemLog_20180620_225011.json
$ cat hostname1_SystemLog_20180620_055337.json
[
    {
        "Created": "2018-06-15T17:57:51.231+00:00", 
        "Message": "The Platform Event Log on system SN# 1234567890 cleared by user REST.", 
        "Name": "LogEntry", 
        "Severity": "OK"
    }, 
    {
        "Created": "2018-06-15T17:57:52.103+00:00", 
        "Message": "The Audit Event Log on system SN# 1234567890 cleared by user REST.", 
        "Name": "LogEntry", 
        "Severity": "OK"
    }, 
    {
        "Created": "2018-06-15T18:06:41.381+00:00", 
        "Message": "Sensor Phy Presence Set has transitioned from normal to non-critical state.", 
        "Name": "LogEntry", 
        "Severity": "Warning"
    }, 
]
```

These files are in the format *{{bmc_ip}}_{{datatype}}_{{datestamp}}* and each contains valuable server information. 

All server data is returned in JSON format and where appropriate it is extracted into an easy-to-read format. In this case, the file *hostname1_SystemLog_20180620_055337.json* contains server data that has already been parsed for consumption.

## Parsing through JSON files

All data collected from servers is returned in JSON format. Any JSON parser can then be used to extract the specific data you are looking for, which can come in handy since in some cases the amount of data collected can be more than you need.

The [jq](https://stedolan.github.io/jq/) parser to be easy to install and use, here are some examples using the output files above:

```bash
$ jq '.[] | .Message' 10.245.39.185_SystemLog_20180620_055337.json
"The Platform Event Log on system SN# 1234567890 cleared by user REST."
"The Audit Event Log on system SN# 1234567890 cleared by user REST."
"Sensor Phy Presence Set has transitioned from normal to non-critical state."
"Sensor Phy Presence Set has deasserted the transition from normal to non-critical state."


$ jq '.[] | .Severity' 10.245.39.185_SystemLog_20180620_055337.json 
"OK"
"OK"
"Warning"
"OK"
"Warning"
```

It should be straight-forward to extract the same data from hundreds of files using shell scripts and organize it accordingly. In the near future scripts will be made available to facilitate data orgnization. For additional help with qt, refer to this [manual](https://shapeshed.com/jq-json/).


## Support

If you run into any problems or would like to provide feedback, please open an issue:
[here](https://github.com/lenovo/python-redfish-lenovo/issues)

