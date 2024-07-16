import meraki
import os
import json
import time
import pandas as pd
import numpy

api_key = os.environ['MERAKI_DASHBOARD_API_KEY']
org_id = os.environ['ORG_ID']


#creates network and enables VLANs
def createNetwork(dashboard, network):
    response = dashboard.organizations.createOrganizationNetwork(org_id, network['name'],network['productTypes'])
    network_id=response['id']
    response = dashboard.appliance.updateNetworkApplianceVlansSettings(network_id, vlansEnabled = True)

    return network_id

def addVlans(dashboard, network):

    vlan = {
        "id": "1234",
        "name": "VLAN",
        "subnet": "192.168.1.0/24",
        "applianceIp": "192.168.1.2",
    }

    response = dashboard.appliance.createNetworkApplianceVlan(network, vlan['id'], vlan['name'], subnet=vlan['subnet'],applianceIp=vlan['applianceIp'])

    return response

def deployVlans(dashboard, networkid, interface):
    

    iface_json = json.loads(f'"{interface}"')

    print(json.dumps(iface_json, indent=2))
    print('tricks')
    vlan = {

        interface['int_id'][-1]

    }


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
            #deployVlans(dashboard, networkid, interface = row[1]['interfaces'])
            currdev = dev



def main():
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