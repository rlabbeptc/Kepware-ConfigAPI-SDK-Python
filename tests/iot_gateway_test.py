# -------------------------------------------------------------------------
# Copyright (c) PTC Inc. All rights reserved.
# See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# IoT Gateway Test - Test to exersice all IoT Gateway related features

from kepconfig.error import KepError
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import kepconfig
import kepconfig.connectivity
import kepconfig.iot_gateway
import json
import time
import datetime
import pytest


# IoT Gateway configs to be used
mqtt_agent_name = 'MQTT'
rest_agent_name = 'REST Client'
rserver_agent_name = 'REST Server'
twx_agent_name = 'Thingworx'
iot_item_name ="System__Date"

# used to test which agents are installed to test against.
agent_list_avail = []

agent_list = []

agent_data = {
            "common.ALLTYPES_NAME": 'TempName',
            "iot_items":[
                {
                "common.ALLTYPES_NAME": "_System_Time",
                "common.ALLTYPES_DESCRIPTION": "",
                "iot_gateway.IOT_ITEM_SERVER_TAG": "_System._Time",
                "iot_gateway.IOT_ITEM_USE_SCAN_RATE": True,
                "iot_gateway.IOT_ITEM_SCAN_RATE_MS": 1000,
                "iot_gateway.IOT_ITEM_SEND_EVERY_SCAN": False,
                "iot_gateway.IOT_ITEM_DEADBAND_PERCENT": 0,
                "iot_gateway.IOT_ITEM_ENABLED": True,
                "iot_gateway.IOT_ITEM_DATA_TYPE": 5 
                }
            ]
            
        }

iot_item_data = {
                "common.ALLTYPES_NAME": iot_item_name,
                "common.ALLTYPES_DESCRIPTION": "",
                "iot_gateway.IOT_ITEM_SERVER_TAG": "_System._Date",
                "iot_gateway.IOT_ITEM_USE_SCAN_RATE": True,
                "iot_gateway.IOT_ITEM_SCAN_RATE_MS": 1000,
                "iot_gateway.IOT_ITEM_SEND_EVERY_SCAN": False,
                "iot_gateway.IOT_ITEM_DEADBAND_PERCENT": 0,
                "iot_gateway.IOT_ITEM_ENABLED": True,
                "iot_gateway.IOT_ITEM_DATA_TYPE": 5 
                }

def HTTPErrorHandler(err):
    if err.__class__ is kepconfig.error.KepHTTPError:
        print(err.code)
        print(err.msg)
        print(err.url)
        print(err.hdrs)
        print(err.payload)
    else:
        print('Different Exception Received: {}'.format(err))

def initialize(server: kepconfig.connection.server):
    try:
        agent_list_avail = server._config_get(server.url +"/project/_iot_gateway?content=type_definition").payload
        for agent in agent_list_avail['child_collections']:
            if agent == 'mqtt_clients': agent_list.append([mqtt_agent_name, kepconfig.iot_gateway.MQTT_CLIENT_AGENT])
            if agent == 'rest_clients': agent_list.append([rest_agent_name, kepconfig.iot_gateway.REST_CLIENT_AGENT])
            if agent == 'rest_servers': agent_list.append([rserver_agent_name, kepconfig.iot_gateway.REST_SERVER_AGENT])
    except Exception as err:
        pytest.skip("IoT gateway plug-in is not installed", allow_module_level=True)

def complete(server):
    # Delete all Agents
    for agent_type in agent_list:
        try:
            agent_left = kepconfig.iot_gateway.agent.get_all_iot_agents(server, agent_type[1])
            for x in agent_left:
                print(kepconfig.iot_gateway.agent.del_iot_agent(server,x['common.ALLTYPES_NAME'],agent_type[1]))
        except Exception as err:
            HTTPErrorHandler(err)

@pytest.fixture(scope="module")
def server(kepware_server):
    server = kepware_server[0]
    global server_type
    server_type = kepware_server[1]
    
    # Initialize any configuration before testing in module
    initialize(server)

    # Everything below yield is run after module tests are completed
    yield server
    complete(server)

def test_agent_add(server):
    for agent_name, agent_type in agent_list:
        # Add Agent
        agent = agent_data.copy()
        agent['common.ALLTYPES_NAME'] = agent_name

        assert kepconfig.iot_gateway.agent.add_iot_agent(server, agent, agent_type)
        
        # Add Agent without Agent Type (error)
        agent['common.ALLTYPES_NAME'] = agent_name + "1"
        with pytest.raises(KepError):
            assert kepconfig.iot_gateway.agent.add_iot_agent(server, agent)

        # Add Agent with bad name (HTTP 207 return with list)
        agent = [
            {
            "common.ALLTYPES_NAME": agent_name + "1"
            },
            {
            "common.ALLTYPES_NAME": "_" + agent_name
            }
        ]

        assert type(kepconfig.iot_gateway.agent.add_iot_agent(server, agent, agent_type)) == list

def test_agent_modify(server):
    for agent_name, agent_type in agent_list:
        # Modify Agent
        agent = {}
        agent['common.ALLTYPES_DESCRIPTION'] = 'This is the test agent created'
        assert kepconfig.iot_gateway.agent.modify_iot_agent(server,agent, agent= agent_name, agent_type= agent_type)

        # Modify Agent with name and type in data
        agent = {}
        agent['common.ALLTYPES_DESCRIPTION'] = 'This is the test agent created'
        agent['common.ALLTYPES_NAME'] = agent_name
        agent['iot_gateway.AGENTTYPES_TYPE'] = agent_type
        assert kepconfig.iot_gateway.agent.modify_iot_agent(server,agent, agent= agent_name, agent_type= agent_type)

        # Modify Agent without type (error)
        agent = {}
        agent['common.ALLTYPES_DESCRIPTION'] = 'This is the test agent created'
        with pytest.raises(KepError):
            assert kepconfig.iot_gateway.agent.modify_iot_agent(server,agent, agent= agent_name)
        
        # Modify Agent without name (error)
        agent = {}
        agent['common.ALLTYPES_DESCRIPTION'] = 'This is the test agent created'
        with pytest.raises(KepError):
            assert kepconfig.iot_gateway.agent.modify_iot_agent(server,agent, agent_type= agent_type)
        
def test_agent_get(server):
    for agent_name, agent_type in agent_list:
        # Get Agent
        assert type(kepconfig.iot_gateway.agent.get_iot_agent(server, agent_name, agent_type)) == dict

        # Get All Agents
        assert type(kepconfig.iot_gateway.agent.get_all_iot_agents(server, agent_type)) == list

        # Test Get with Options
        # Get All Agents
        ret = kepconfig.iot_gateway.agent.get_all_iot_agents(server, agent_type, options= {'filter': '1'})
        assert type(ret) == list
        assert len(ret) == 1

def test_iot_item_add(server):       
    for agent_name, agent_type in agent_list:
        # Add Iot Item
        assert kepconfig.iot_gateway.iot_items.add_iot_item(server, iot_item_data, agent_name, agent_type)
        
        # Add Iot Items with one failed
        
        iot_item_data2 = [
            {
                "common.ALLTYPES_NAME": iot_item_name + "1",
                "common.ALLTYPES_DESCRIPTION": "",
                "iot_gateway.IOT_ITEM_SERVER_TAG": "_System._Time_Minute",
                "iot_gateway.IOT_ITEM_USE_SCAN_RATE": True,
                "iot_gateway.IOT_ITEM_SCAN_RATE_MS": 1000,
                "iot_gateway.IOT_ITEM_SEND_EVERY_SCAN": False,
                "iot_gateway.IOT_ITEM_DEADBAND_PERCENT": 0,
                "iot_gateway.IOT_ITEM_ENABLED": True,
                "iot_gateway.IOT_ITEM_DATA_TYPE": 5 
            },
            {
                "common.ALLTYPES_NAME": iot_item_name,
                "common.ALLTYPES_DESCRIPTION": "",
                "iot_gateway.IOT_ITEM_SERVER_TAG": "_System._Time_Seconds",
                "iot_gateway.IOT_ITEM_USE_SCAN_RATE": True,
                "iot_gateway.IOT_ITEM_SCAN_RATE_MS": 1000,
                "iot_gateway.IOT_ITEM_SEND_EVERY_SCAN": False,
                "iot_gateway.IOT_ITEM_DEADBAND_PERCENT": 0,
                "iot_gateway.IOT_ITEM_ENABLED": True,
                "iot_gateway.IOT_ITEM_DATA_TYPE": 5 
            }
        ]
        assert type(kepconfig.iot_gateway.iot_items.add_iot_item(server, iot_item_data2, agent_name, agent_type)) == list
        
def test_iot_item_modify(server):
    for agent_name, agent_type in agent_list:
        # Modify IoT Item
        modify_iot_item = {
                "common.ALLTYPES_NAME": iot_item_name,
                "common.ALLTYPES_DESCRIPTION": "Modified the IoT Item"
        }
        assert kepconfig.iot_gateway.iot_items.modify_iot_item(server, modify_iot_item, agent_name, agent_type)

        # Modify IoT Item v 2
        modify_iot_item = {
                "iot_gateway.IOT_ITEM_SCAN_RATE_MS": 2000,
        }
        assert kepconfig.iot_gateway.iot_items.modify_iot_item(server, modify_iot_item, agent_name, agent_type, iot_item=iot_item_name, force = True)

def test_iot_item_get(server):        
    for agent_name, agent_type in agent_list:
        # Read IoT Item
        assert type(kepconfig.iot_gateway.iot_items.get_iot_item(server, iot_item_name, agent_name, agent_type)) == dict

        # Read All IoT Items
        assert type(kepconfig.iot_gateway.iot_items.get_all_iot_items(server, agent_name, agent_type)) == list

        # Test Get with Options
        # Read All IoT Items
        ret = kepconfig.iot_gateway.iot_items.get_all_iot_items(server, agent_name, agent_type, options= {'filter': 'Date'})
        assert type(ret) == list
        assert len(ret) == 1

def test_iot_item_del(server):        
    for agent_name, agent_type in agent_list:
        # Delete IoT Item
        assert kepconfig.iot_gateway.iot_items.del_iot_item(server, iot_item_name, agent_name, agent_type)

def test_agent_del(server):
    for agent_name, agent_type in agent_list:
        # Delete IoT Agent
        assert kepconfig.iot_gateway.agent.del_iot_agent(server, agent_name, agent_type)