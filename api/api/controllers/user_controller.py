# Copyright (C) 2015-2019, Wazuh Inc.
# Created by Wazuh, Inc. <info@wazuh.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

import asyncio
import logging
import re

import connexion
from api.authentication import decode_token

from wazuh import user_manager
from wazuh.cluster.dapi.dapi import DistributedAPI
from wazuh.exception import WazuhError
from ..util import remove_nones_to_dict, exception_handler, raise_if_exc

logger = logging.getLogger('wazuh')
loop = asyncio.get_event_loop()
auth_re = re.compile(r'basic (.*)', re.IGNORECASE)


@exception_handler
def get_users():
    """Get username of a specified user

    :return: All users data
    """
    dapi = DistributedAPI(f=user_manager.get_users,
                          request_type='local_master',
                          is_async=False,
                          logger=logger
                          )
    data = raise_if_exc(loop.run_until_complete(dapi.distribute_function()))

    return data, 200


@exception_handler
def get_user(username=None):
    """Get username of a specified user

    :param username: Username of an user
    :return: User data
    """
    f_kwargs = {'username': username}

    dapi = DistributedAPI(f=user_manager.get_user_id,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          logger=logger
                          )
    data = raise_if_exc(loop.run_until_complete(dapi.distribute_function()))

    return data, 200


@exception_handler
def check_body(f_kwargs, keys: list = None):
    """Checks that body is correct

    :param f_kwargs: Body to be checked
    :param keys: Keys that the body must have only and exclusively
    :return: 0 -> Correct | str -> Incorrect
    """
    if keys is None:
        keys = ['username', 'password']
    for key in f_kwargs.keys():
        if key not in keys:
            return key

    return 0


@exception_handler
def create_user():
    """Create a new user

    :return: User data
    """
    f_kwargs = {**{}, **connexion.request.get_json()}
    process = check_body(f_kwargs)
    if process != 0:
        raise WazuhError(5005, extra_message='Invalid field found {}'.format(process))

    dapi = DistributedAPI(f=user_manager.create_user,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          logger=logger
                          )
    data = raise_if_exc(loop.run_until_complete(dapi.distribute_function()))

    return data, 200


@exception_handler
def update_user(username=None):
    """Modify an existent user

    :param username: Name of the user to be modified
    :return: User data
    """
    user_info = decode_token(connexion.request.headers['Authorization'][7:])
    f_kwargs = {'username': username, **{}, **connexion.request.get_json()}
    process = check_body(f_kwargs)
    if process != 0:
        raise WazuhError(5005, extra_message='Invalid field found {}'.format(process))

    dapi = DistributedAPI(f=user_manager.update_user,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          logger=logger
                          )
    data = raise_if_exc(loop.run_until_complete(dapi.distribute_function()))

    return data, 200


@exception_handler
def delete_user(username=None):
    """Delete an existent user

    :param username: Name of the user to be removed
    :return: Result of the operation
    """
    f_kwargs = {'username': username}

    dapi = DistributedAPI(f=user_manager.delete_user,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          logger=logger
                          )
    data = raise_if_exc(loop.run_until_complete(dapi.distribute_function()))

    return data, 200
