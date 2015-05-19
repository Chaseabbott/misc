#!/usr/bin/python
# 
 
import argparse
import json
import logging
import sys
 
import restapi;
 
DEFAULT_BIGIQ_USER = "admin"
DEFAULT_BIGIQ_PASSWORD = "admin"
DEFAULT_BIGIQ_ACTION = "List"
DEFAULT_BIGIQ_TENANT_NAME = "My-Tenant"
DEFAULT_BIGIQ_CONNECTOR_NAME = "My-Tenant-Connector"
DEFAULT_BIGIQ_TENANT_USER= "MyTenant"
LOG = logging.getLogger(__name__)
 
##
# Loads a JSON file.
def load_json_file(name):
   
    with file(name) as f:
        json_data = json.load(f)
    
    if json_data:
        json_data = json.dumps(json_data)
        
    return json_data
    
# Prints a line separator (for easy viewing).
def print_separator():
        print("-" * 80)
    
##
# Validates the HTTP/REST result.
def validate_result(result, verbose=False):
       
    # Any result beyond HTTP 400 is considered an error.
    if ((result == None) or (result[0] >= restapi.HTTP_400)):
        sys.exit(1)
    
    if verbose:
        for i in range (1, len(result)):
	    LOG.info(result[i])
 
##
# Modifies a field of a JSON string and returns it as a string
def modify_json(json_string, field_to_modify, new_value):
 
    json_data = json.loads(json_string)
 
    if json_data == None:
        sys.exit(1)
 
    json_data[field_to_modify] = new_value
 
    return json.dumps(json_data)
 
#Retrieve connector link to include it into the tenant to be created
def retrieve_connector_link(list_connectors, connector_name):
    result = []
    for i in range (1, len(list_connectors)):
        connector_name_ = list_connectors[i]['items'][0]['name']
        if (connector_name == connector_name_):
                connector_link = {'link':list_connectors[i]['items'][0]['selfLink']}
                result.append(connector_link)
                print(result)
		return(result)
 
##
# Runs the BIG-IQ cloud API test suite.
def run_bigiq_tests(bigiq_address,
                    action=DEFAULT_BIGIQ_ACTION,
		    tenant_name=DEFAULT_BIGIQ_TENANT_NAME,
		    connector_name=DEFAULT_BIGIQ_CONNECTOR_NAME,
		    tenant_user=DEFAULT_BIGIQ_TENANT_USER,
		    bigiq_user=DEFAULT_BIGIQ_USER,
                    bigiq_password=DEFAULT_BIGIQ_PASSWORD,
                    verbose=False):
    
    LOG.info("Running BIG-IQ Tenant tests...")
    # Initialize cloud API tester.
    LOG.info("BIG-IQ: Initializing cloud API shim...")
    cloud_api = restapi.RestApi(host=bigiq_address,
                               user=bigiq_user,
                               password=bigiq_password)
    LOG.info("BIG-IQ: Cloud API shim successfully initialized.")
    
    if (action == "Delete"):
    	result = cloud_api.delete_tenant(tenant_name)
	validate_result(result, verbose)
	LOG.info("BIG-IQ: Tenant successfully deleted")
 
    if (action == "List"):
    	# BIG-IQ: query tenants list
    	LOG.info("BIG-IQ: Querying list of tenants...")
    	result = cloud_api.get_all_tenants()
	validate_result(result, True)
    	LOG.info("BIG-IQ: Device tenant list successfully retrieved.")
 	
    if (action == "Create"):
    	# BIG-IQ: create tenant.
    	LOG.info("BIG-IQ: Creating tenant...")
	
	# BIG-IQ: Retrieve connetor link
	list_connectors = cloud_api.get_local_connectors()
	local_connector_link = retrieve_connector_link(list_connectors, connector_name)
	
	# BIG-IQ: Retieve user link
	user_information = cloud_api.get_user(tenant_user)
	print(user_information)
	user_information_link = {'link':user_information[1]['selfLink']}
	print(user_information_link)
	# BIG-IQ: Define the user role for this partition ... done by appending CloudTenantAdministrator to the tenant name
	user_role_link = {'link':'https://localhost/mgmt/shared/authz/roles/CloudTenantAdministrator_' + tenant_name}
	print(user_role_link)
	tenant_json_string = modify_json(load_json_file("./bigiq_create_tenant.json"),
                                         'cloudConnectorReferences',
                                         local_connector_link)
	tenant_json_string = modify_json(tenant_json_string,
                                         'userReference',
                                         user_information_link)
	tenant_json_string = modify_json(tenant_json_string,
                                         'roleReference',
                                         user_role_link)
    	print (tenant_json_string)
	result = cloud_api.create_tenant(tenant_json_string)
    	validate_result(result, verbose)
    	LOG.info("BIG-IQ: Tenant successfully created.")
   	
# Initializes logging.
def init_logging(level=logging.INFO):
 
    log_format = '%(asctime)-15s: %(funcName)s(): %(message)s'
    logging.basicConfig(format=log_format, level=level)
 
##
# Main entry point
def main():
    
    parser = argparse.ArgumentParser(description="Runs various REST-API functional tests")
    
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('--tenant-name', default=DEFAULT_BIGIQ_TENANT_NAME)
    parser.add_argument('--connector-name', default=DEFAULT_BIGIQ_CONNECTOR_NAME)
    parser.add_argument('--tenant-user', default=DEFAULT_BIGIQ_TENANT_USER)
    parser.add_argument('--bigiq-address', required=True)
    parser.add_argument('--bigiq-user', default=DEFAULT_BIGIQ_USER)
    parser.add_argument('--bigiq-password', default=DEFAULT_BIGIQ_PASSWORD)
    parser.add_argument('--action', default=DEFAULT_BIGIQ_ACTION)
 
    args = parser.parse_args()
    
    log_level = logging.INFO
    
    if (args.verbose):
        log_level = logging.DEBUG
        
    init_logging(log_level)
    
    # BIG-IQ tests.
    run_bigiq_tests(bigiq_address=args.bigiq_address,
                    action=args.action,
		    tenant_name=args.tenant_name,
		    connector_name=args.connector_name,
		    tenant_user=args.tenant_user,
		    bigiq_user=args.bigiq_user,
                    bigiq_password=args.bigiq_password,
                    verbose=args.verbose)
    
    LOG.info("OK. Done testing.")
 
##
# Main entry point launcher.
if __name__ == '__main__':
    main()