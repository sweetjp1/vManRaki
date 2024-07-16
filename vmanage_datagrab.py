import requests
import logging
import json

logger=logging.getLogger(__name__)
vmanage_host='10.10.20.90'
vmanage_port='8443'
vmanage_username='admin'
vmanage_password='C1sco12345'


class Authentication:

    @staticmethod
    def get_jsessionid(vmanage_host, vmanage_port, username, password):
        api = "/j_security_check"
        base_url = "https://%s:%s"%(vmanage_host, vmanage_port)
        url = base_url + api
        payload = {'j_username' : username, 'j_password' : password}
        
        response = requests.post(url=url, data=payload, verify=False)
        try:
            cookies = response.headers["Set-Cookie"]
            jsessionid = cookies.split(";")
            return(jsessionid[0])
        except:
            if logger is not None:
                logger.error("No valid JSESSION ID returned\n")
            exit()

    @staticmethod
    def get_token(vmanage_host, vmanage_port, jsessionid):
       headers = {'Cookie': jsessionid}
       base_url = "https://%s:%s"%(vmanage_host, vmanage_port)
       api = "/dataservice/client/token"
       url = base_url + api      
       try:
           response = requests.get(url=url, headers=headers, verify=False)
           if response.status_code == 200:
               return(response.text)
           else:
               return None
       except:
           if logger is not None:
               logger.error("No valid token returned\n")
           exit()


def getDevices(base_url, header):
    url= base_url + '/device'
    payload = {}
    response=requests.request("GET", url, headers=header, data=payload, verify=False)
    return response.json()
    exit()

def parseVEdge(device_json):

    devices = list()

    for d in device_json['data']:
        if d['device-type'] == 'vedge':
            dev_name = d['host-name']
            dev_id = d['uuid']
            dev_lastupdated = d['lastupdated']
            dev_reachability = d['reachability']
            device = { 'dev_name':dev_name, 'dev_id':dev_id, 'dev_lastupdated':dev_lastupdated, 'dev_reachability':dev_reachability }
            devices.append(device)
    return devices

def main():

    #authenticate and generate a baseurl + headers
    logging.basicConfig(filename='grabber.log', level=logging.INFO)
    Auth = Authentication()
    jsessionid = Auth.get_jsessionid(vmanage_host,vmanage_port,vmanage_username,vmanage_password)
    token = Auth.get_token(vmanage_host, vmanage_port, jsessionid)

    if token is not None:
        header = {'Content-Type': "application/json",'Cookie': jsessionid, 'X-XSRF-TOKEN': token}
    else:
        header = {'Content-Type': "application/json",'Cookie': jsessionid}

    base_url = "https://%s:%s/dataservice"%(vmanage_host, vmanage_port)
    
    device_json = getDevices(base_url, header)
    vedge_list= parseVEdge(device_json)
    print(json.dumps(vedge_list, indent=4))

            

    




if __name__ == '__main__':
    main()