# -------------------------------------------------------------------------
# Copyright (c) PTC Inc. and/or all its affiliates. All rights reserved.
# See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


r"""`exchange` exposes an API to allow modifications (add, delete, modify) to 
exchange objects for EGD devices within the Kepware Configuration API
"""

from ... import path_split
from ...connection import server
from ...error import KepHTTPError, KepError
from typing import Union
from .. import egd as EGD, channel, device

CONSUMER_ROOT = '/consumer_exchange_groups/consumer exchanges/consumer_exchanges'
PRODUCER_ROOT = '/producer_exchange_groups/producer exchanges/producer_exchanges'

def _create_url(device_path, ex_type, exchange_name = None):
    '''Creates url object for the "exchange" branch of Kepware's project tree. Used 
    to build a part of Kepware Configuration API URL structure

    Returns the exchange specific url when a value is passed as the exchange name.
    '''
    path_obj = path_split(device_path)
    device_root = channel._create_url(path_obj['channel']) + device._create_url(path_obj['device'])

    if exchange_name == None:
        if ex_type.upper() == EGD.CONSUMER_EXCHANGE:
            return device_root + CONSUMER_ROOT
        else:
            return device_root + PRODUCER_ROOT
    else:
        if ex_type.upper() == EGD.CONSUMER_EXCHANGE:
            return '{}{}/{}'.format(device_root,CONSUMER_ROOT,exchange_name)
        else:
            return '{}{}/{}'.format(device_root,PRODUCER_ROOT,exchange_name)

def add_exchange(server: server, device_path: str, ex_type: str, DATA: Union[dict, list]) -> Union[bool, list]:
    '''Add a `"exchange"` or multiple `"exchange"` objects to Kepware. Can be used to pass children of a exchange object 
    such as ranges. This allows you to create a exchange and ranges for the exchange all in one function, if desired.

    Additionally it can be used to pass a list of exchanges and it's children to be added all at once.

    :param server: instance of the `server` class
    :param device_path: path to EGD device with exchanges. Standard Kepware address decimal 
    notation string such as `"channel1.device1"`
    :param ex_type: type of exchange, either `CONSUMER` or `PRODUCER`
    :param DATA: Dict or List of Dicts of the exchange(s) and it's children
    expected by Kepware Configuration API

    :return: True - If a "HTTP 201 - Created" is received from Kepware server
    :return: If a "HTTP 207 - Multi-Status" is received from Kepware with a list of dict error responses for all 
    exchanges added that failed.
        
    :raises KepHTTPError: If urllib provides an HTTPError
    :raises KepURLError: If urllib provides an URLError
    '''

    r = server._config_add(server.url + _create_url(device_path, ex_type), DATA)
    if r.code == 201: return True
    elif r.code == 207:
        errors = [] 
        for item in r.payload:
            if item['code'] != 201:
                errors.append(item)
        return errors
    else: 
        raise KepHTTPError(r.url, r.code, r.msg, r.hdrs, r.payload)

def del_exchange(server: server, device_path: str, ex_type: str, exchange_name: str) -> bool:
    '''Delete an `"exchange"` object in Kepware. This will delete all children as well
    
    :param server: instance of the `server` class
    :param device_path: path to EGD device with exchanges. Standard Kepware address decimal 
    notation string such as `"channel1.device1"`
    :param ex_type: type of exchange, either `CONSUMER` or `PRODUCER`
    :param exchange_name: name of exchange to delete
    
    :return: True - If a "HTTP 200 - OK" is received from Kepware server

    :raises KepHTTPError: If urllib provides an HTTPError
    :raises KepURLError: If urllib provides an URLError
    '''

    r = server._config_del(server.url + _create_url(device_path, ex_type, exchange_name))
    if r.code == 200: return True 
    else: raise KepHTTPError(r.url, r.code, r.msg, r.hdrs, r.payload)

def modify_exchange(server: server, device_path: str, ex_type: str, DATA: dict, *, exchange_name: str = None, force: bool = False) -> bool:
    '''Modify a `"exchange"` object and it's properties in Kepware. If a `"exchange_name"` is not provided as an input,
    you need to identify the exchange in the *'common.ALLTYPES_NAME'* property field in the `"DATA"`. It will 
    assume that is the exchange that is to be modified.

    :param server: instance of the `server` class
    :param device_path: path to EGD device with exchanges. Standard Kepware address decimal 
    notation string such as `"channel1.device1"`
    :param DATA: Dict of the exchange properties to be modified.
    :param ex_type: type of exchange, either `CONSUMER` or `PRODUCER`
    :param exchange_name: *(optional)* name of exchange to modify. Only needed if not existing in `"DATA"`
    :param force: *(optional)* if True, will force the configuration update to the Kepware server
    
    :return: True - If a "HTTP 200 - OK" is received from Kepware server

    :raises KepHTTPError: If urllib provides an HTTPError
    :raises KepURLError: If urllib provides an URLError
    '''
    
    exchange_data = server._force_update_check(force, DATA)
    if exchange_name == None:
        try:
            r = server._config_update(server.url + _create_url(device_path, ex_type, exchange_data['common.ALLTYPES_NAME']), exchange_data)
            if r.code == 200: return True 
            else: raise KepHTTPError(r.url, r.code, r.msg, r.hdrs, r.payload)
        except KeyError as err:
            err_msg = f'Error: No exchange identified in DATA | Key Error: {type(DATA)}'
            raise KepError(err_msg) 
    else:
        r = server._config_update(server.url + _create_url(device_path, ex_type, exchange_name), exchange_data)
        if r.code == 200: return True 
        else: raise KepHTTPError(r.url, r.code, r.msg, r.hdrs, r.payload)

def get_exchange(server: server, device_path: str, ex_type: str, exchange_name: str = None, *, options: dict = None) -> Union[dict, list]:
    '''Returns the properties of the exchange object or a list of all exchanges and their 
    properties for the type input. Returned object is JSON.
    
    :param server: instance of the `server` class
    :param device_path: path to EGD device with exchanges. Standard Kepware address decimal 
    notation string such as `"channel1.device1"`
    :param ex_type: type of exchange, either `CONSUMER` or `PRODUCER`
    :param exchange_name: *(optional)* name of exchange. If not defined, get all exchanges
    :param options: *(optional)* Dict of parameters to filter, sort or pagenate the list of exchanges. Options are 'filter', 
    'sortOrder', 'sortProperty', 'pageNumber', and 'pageSize'. Only used when exchange_name is not defined.
    
    :return: Dict of properties for the exchange requested or a List of exchanges and their properties

    :raises KepHTTPError: If urllib provides an HTTPError
    :raises KepURLError: If urllib provides an URLError
    '''
    if exchange_name == None:
        r = server._config_get(f'{server.url}{_create_url(device_path, ex_type)}', params= options)
    else:
        r = server._config_get(f'{server.url}{_create_url(device_path, ex_type, exchange_name)}')
    return r.payload

def get_all_exchanges(server: server, device_path: str, *, options: dict = None) -> list[list, list]:
    '''Returns list of all `"exchange"` objects (both CONSUMER and PRODUCER) and their properties. Returned object is JSON list.
    
    INPUTS:
    :param server: instance of the `server` class
    :param device_path: path to EGD device with exchanges. Standard Kepware address decimal 
    notation string such as `"channel1.device1"`
    :param options: *(optional)* Dict of parameters to filter, sort or pagenate the list of exchanges. Options are 'filter', 
    'sortOrder', 'sortProperty', 'pageNumber', and 'pageSize'. Only used when exchange_name is not defined.
    
    :return: List - [list of consumer exchanges, list of producer exchanges] - list of lists for all 
    exchanges for the device

    :raises KepHTTPError: If urllib provides an HTTPError
    :raises KepURLError: If urllib provides an URLError
    '''
    exchange_list = []
    exchange_list.append(get_exchange(server, device_path, EGD.CONSUMER_EXCHANGE, options= options))
    exchange_list.append(get_exchange(server, device_path, EGD.PRODUCER_EXCHANGE, options= options))
    return exchange_list