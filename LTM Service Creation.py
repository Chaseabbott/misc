import requests, json
 
# define program-wide variables
BIGIP_ADDRESS = '192.168.100.1'
BIGIP_USER = 'admin'
BIGIP_PASS = 'admin'
 
VS_NAME = 'VS_Demo_DC1'
VS_ADDRESS = '172.16.1.1'
VS_PORT = '0'
 
RULE_NAME = 'Rule_Demo_'
RULE_CONTENT = 'when CLIENT_ACCEPTED { if { not ([class match [TCP::local_port] eq DG_Demo]) } { drop } }'
DATAGROUP_NAME = ' DG_Demo'
DATAGROUP_CONTENT = [ '80', '81', '82' ]
 
POOL_NAME = 'Pool_Demo'
POOL_LB_METHOD = 'least-connections-member'
POOL_MEMBERS = [ '192.168.100.200:80', '192.168.100.200:8080', '192.168.100.201:80', '192.168.100.201:8080' ]
 
 
#Create DataGroup
def create_dg(bigip, name):
	payload = {}
 
	payload['name'] = name
	payload['type'] = 'string'
	payload['records'] = [ { 'name' : record } for record in DATAGROUP_CONTENT ]
	bigip.post('%s/ltm/data-group/internal' % BIGIP_URL_BASE, data=json.dumps(payload))
 
#Create iRule
def create_irule(bigip,name,content):
	payload = {}
 
        payload['name'] = name
        payload['apiAnonymous'] = RULE_CONTENT
        bigip.post('%s/ltm/rule' % BIGIP_URL_BASE, data=json.dumps(payload))
 
# create/delete methods
def create_pool(bigip, name, members, lb_method):
	payload = {}
 
	# convert member format
	members = [ { 'description' : 'Added through python REST script', 'name' : member } for member in POOL_MEMBERS ]
 
	# define test pool
	payload['name'] = name
	payload['description'] = 'A Python REST client test pool'
	payload['loadBalancingMode'] = lb_method
	payload['monitor'] = 'http'
	payload['members'] = members
	bigip.post('%s/ltm/pool' % BIGIP_URL_BASE, data=json.dumps(payload))
 
def create_http_virtual(bigip, name, address, port, pool):
	payload = {}
 
	# define test virtual
	payload['name'] = name
	payload['description'] = 'A Python REST client test virtual server'
	payload['destination'] = '%s:%s' % (address, port)
	payload['mask'] = '255.255.255.255'
	payload['ipProtocol'] = 'tcp'
	payload['sourceAddressTranslation'] = { 'type' : 'automap' }
	payload['profiles'] = [ 
		{ 'kind' : 'ltm:virtual:profile', 'name' : 'http' }, 
		{ 'kind' : 'ltm:virtual:profile', 'name' : 'tcp' }
	]
	payload['pool'] = pool
	payload['rules'] = [ '/Common/%s' % RULE_NAME ]
	bigip.post('%s/ltm/virtual' % BIGIP_URL_BASE, data=json.dumps(payload))
 
def delete_pool(bigip, name):
	bigip.delete('%s/ltm/pool/%s' % (BIGIP_URL_BASE, name))
 
def delete_virtual(bigip, name):
	bigip.delete('%s/ltm/virtual/%s' % (BIGIP_URL_BASE, name))
 
# REST resource for BIG-IP that all other requests will use
bigip = requests.session()
bigip.auth = (BIGIP_USER, BIGIP_PASS)
bigip.verify = False
bigip.headers.update({'Content-Type' : 'application/json'})
print "created REST resource for BIG-IP at %s..." % BIGIP_ADDRESS
 
# Requests requires a full URL to be sent as arg for every request, define base URL globally here
BIGIP_URL_BASE = 'https://%s/mgmt/tm' % BIGIP_ADDRESS
 
#create datagroup
create_dg(bigip, DATAGROUP_NAME)
 
#create iRule
create_irule(bigip, RULE_NAME, RULE_CONTENT)
 
# create pool
create_pool(bigip, POOL_NAME, POOL_MEMBERS, POOL_LB_METHOD)
 
# create virtual
create_http_virtual(bigip, VS_NAME, VS_ADDRESS, VS_PORT, POOL_NAME)