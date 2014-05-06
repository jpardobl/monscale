import requests, logging, simplejson


POOL_URL = "https://{f5_host}/mgmt/tm/ltm/pool/{pool_name}"
POOL_MEMBER_URL = "https://{f5_host}/mgmt/tm/ltm/pool/{pool_name}/members" #https://$hostname/mgmt/tm/ltm/pool/karma1/members


def add_pool_members(f5_host, f5_username, f5_password, pool_name, member_list=[]):
    """
    member_list = ["172.21.185.24:8080", ]
    """
    logging.basicConfig(level=logging.DEBUG)
    #{"members":[{"name":"172.21.185.24:8080" }]}' https://$hostname/mgmt/tm/ltm/pool/karma2
    
    url = POOL_URL.format(f5_host=f5_host, pool_name=pool_name)
    logging.debug("[add_pool_members] url: %s" % url)
    
    old_members = get_pool_members(f5_host, f5_username, f5_password, pool_name)
    old_members += [{"name": x} for x in member_list]
    logging.debug("[add_pool_members] members: %s" % old_members)
    headers = {'content-type': 'application/json'}
    ret = requests.put(url, data=simplejson.dumps({"members": old_members}), headers=headers, auth=(f5_username, f5_password), verify=False)
    print("[add_pool_members] ret: %s" % ret.text)

def del_pool_members(f5_host, f5_username, f5_password, pool_name, member_list=[]):
    """
    member_list = ["172.21.185.24:8080", ]
    """

    url = POOL_URL.format(f5_host=f5_host, pool_name=pool_name)
    logging.debug("[del_pool_members] url: %s" % url)
    
    old_members = get_pool_members(f5_host, f5_username, f5_password, pool_name)
    for x in member_list: old_members.remove(x)
    
    logging.debug("[del_pool_members] members: %s" % old_members)
    headers = {'content-type': 'application/json'}
    ret = requests.put(url, data=simplejson.dumps({"members": old_members}), headers=headers, auth=(f5_username, f5_password), verify=False)
    print("[del_pool_members] ret: %s" % ret.text)

def get_pool_members(f5_host, f5_username, f5_password, pool_name):
    url = POOL_MEMBER_URL.format(f5_host=f5_host, pool_name=pool_name)
    logging.debug("[add_pool_members] url: %s" % url)
    
    headers = {'content-type': 'application/json'}
    ret = requests.get(url, headers=headers, auth=(f5_username, f5_password), verify=False)
    return [ m["name"] for m in ret.json()["items"]]
        