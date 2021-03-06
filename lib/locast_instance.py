"""
MIT License

Copyright (C) 2021 ROCKY4546
https://github.com/rocky4546

This file is part of Cabernet

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.
"""


from lib.plugins.plugin_instance_obj import PluginInstanceObj
import lib.common.utils as utils
import lib.common.exceptions as exceptions
from .authenticate import Authenticate
from .location import Location
from .channels import Channels
from .epg import EPG
from .stream import Stream


class LocastInstance(PluginInstanceObj):

    def __init__(self, _locast, _instance_key):
        super().__init__(_locast, _instance_key)
        self.config_obj = _locast.config_obj
        self.instance_key = _instance_key
        self.plugin_obj = _locast
        if not self.config_obj.data[self.config_section]['enabled']:
            self.enabled = False
            return
        
        if self.plugin_obj.auth.token is None:
            try:
                self.auth = Authenticate(self.config_obj, self.config_section)
                if self.auth.token is None:
                    self.config_obj.data[self.config_section]['enabled'] = False
                self.token = self.auth.token
                self.is_free_account = self.auth.is_free_account
            except exceptions.CabernetException:
                self.logger.error('Setting Locast instance {} to disabled'.format(self.instance_key))
                self.enabled = False
                self.token = None
                self.is_free_account = False
                return
        else:
            self.token = self.plugin_obj.auth.token
            self.is_free_account = self.plugin_obj.auth.is_free_account
        try:
            self.location = Location(self)
        except exceptions.CabernetException:
            self.logger.error('Setting Locast instance {} to disabled'.format(self.instance_key))
            self.enabled = False
            self.token = None
            self.is_free_account = False
            return
        
        self.channels = Channels(self)
        self.stream = Stream(self)
        self.epg = EPG(self)

    def is_time_to_refresh(self, _last_refresh):
        return self.stream.is_time_to_refresh(_last_refresh)


    @property
    def config_section(self):
        return utils.instance_config_section(self.plugin_obj.name, self.instance_key)
