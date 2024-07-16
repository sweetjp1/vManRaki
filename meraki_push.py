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

def main():

    df = pd.read_excel('vEdgeDataPull.xlsx')
    
    for row in df.iterrows():
        print(row[1]['dev_name'])


def main_old():
    print("init")
    dashboard = meraki.DashboardAPI(api_key)

    network = {
        "name": "Main Office3",
        "productTypes": [
            "appliance",
            "switch"
        ],
        "tags": [
            "tag1",
            "tag2"
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