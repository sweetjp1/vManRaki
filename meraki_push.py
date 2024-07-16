import meraki
import os
import json
import time
import pandas as pd
import numpy
import re
import ipaddress


api_key = os.environ['MERAKI_DASHBOARD_API_KEY']
org_id = os.environ['ORG_ID']


#creates network and enables VLANs
def createNetwork(dashboard, network):
    response = dashboard.organizations.createOrganizationNetwork(org_id, network['name'],network['productTypes'])
    network_id=response['id']
    response = dashboard.appliance.updateNetworkApplianceVlansSettings(network_id, vlansEnabled = True)

    return network_id



def addVlans(dashboard, network, vlan):

#If interface ends in 0 assume loopback (Dangerous?)
    if vlan['id'] != '0':
        response = dashboard.appliance.createNetworkApplianceVlan(network, vlan['id'], vlan['name'], subnet=vlan['subnet'],applianceIp=vlan['applianceIp'])
    else:
        response = "Loopback" + vlan['id']
    return response

def deployVlans(dashboard, networkid, interface):
    
    #interface string is messy. pretty up for JSON load.
    iface_json = json.loads(interface.replace('"','').replace("'", '"'))

    #find interface number to use as VLANID, this needs to change to support subinterfaces.
    pat = r"(\d+)(?=\D*$)"
    vlan_id = re.search(pat, iface_json['int_id'])

    #process IPs
    process_iface = ipaddress.IPv4Interface(iface_json['int_ip'])
    
    #create vlan JSON
    vlan = {

        "id": vlan_id[0],
        "name": iface_json['int_desc'],
        "subnet": format(process_iface.network),
        "applianceIp": format(process_iface.ip)

    }
    return vlan

def deployNetworks(excel,dashboard):
    df = pd.read_excel(excel)
    currdev = ""

    for row in df.iterrows():
        if 'LAN' in row[1]['type']:
            dev = row[1]['dev_name']
            if currdev == "" or currdev != dev:
                network ={
                    "name" : dev,
                    "productTypes": [
                        "appliance",
                        "switch"
                    ],
                }
                productTypes = [ "appliance", "switch" ]
                networkid = createNetwork(dashboard, network)
                print(networkid + ": " + dev)
            vlan = deployVlans(dashboard, networkid, interface = row[1]['interfaces'])
            addVlans(dashboard, networkid, vlan)
            currdev = dev



def main():

#    iface =  "{'vpn': '1', 'int_id': 'GigabitEthernet3', 'int_desc': 'port.dc-phys', 'int_ip': '10.10.20.182/24'}"
#    print(json.dumps(iface,indent=2))

#    vlan = deployVlans(dashboard, 0, iface)
#    print(json.dumps(vlan,indent=2))
#    addVlans(dashboard, 0, vlan)
 

    dashboard = meraki.DashboardAPI(api_key)
    deployNetworks('vEdgeDataPull.xlsx', dashboard)
   


def main_old():
    print("init")
    dashboard = meraki.DashboardAPI(api_key)

    network = {
        "name": "Main Office3",
        "productTypes": [
            "appliance",
            "switch"
        ],
        "timeZone": "America/Los_Angeles",
        "notes": "Additional description of the network"
    }

    network_id = createNetwork(dashboard, network=network)
    addVlans(dashboard,network_id)
    response = dashboard.appliance.getNetworkApplianceVlans(network_id)
    print(json.dumps(response, indent=2))

    #cleanup
    dashboard.networks.deleteNetwork(network_id)

if __name__ == '__main__':
    main()