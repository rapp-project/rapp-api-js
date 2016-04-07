#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Copyright 2015 RAPP

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

    #http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Authors: Konstantinos Panayiotou, Manos Tsardoulias
# contact: klpanagi@gmail.com, etsardou@iti.gr


## @file ServiceController/ServiceControllerSync.py
#
#  @copyright Rapp Projecty EU 2015
#  @author Konstantinos Panayiotou, [klpanagi@gmail.com]
#

import requests
# from requests.auth import HTTPBasicAuth  # Http basic authentication
from requests.exceptions import *  # Requests Exceptions
import json
from os import path
import sys
from ConfigParser import SafeConfigParser



__path__ = path.dirname(__file__)


class ServiceControllerBase(object):
  ##
  #  @brief Object constructor
  #
  def __init__(self, connection=None):
    self.cfgDir_ = path.join(__path__, '../config')
    self.connection_ = {
      "protocol": "",
      "ipaddr": "",
      "port": ""
    }

    if connection is not None:
      self.connection_ = connection
    else:
      self.__parse_platform_cfg()


  ##
  #  Check if a dic is represented in json string format.
  #  @param obj dictionary
  #
  def is_json(self, obj):
    try:
      json.loads(obj)
    except ValueError:
      return False
    return True


  ##
  #  Make file tuples for multipart/form-data http/s requests.
  #  @param filepath The path to the file.
  #  @param optional Http field name value.
  #
  #  {httpFieldName: {filename: '', file descriptor: }}
  #
  def _make_file_tuple(self, filepath, httpField='file' ):
    filename = self.__basename(filepath)
    tuple_ = (httpField, (filename, open(filepath, 'rb')))
    return tuple_


  ##
  #  @brief Make payload tuple for multipart/form-data http/s requests.
  #  @param payload Data payload - dictionary.
  #  @param httpField Optional http field name value.
  #
  #  {httpFieldName: {filename: '', file descriptor: }}
  #
  def _make_payload_dic(self, payload, httpField='' ):
    if httpField == '':
      httpField = 'json'
    dic = {httpField: json.dumps(payload)}
    return dic


  def run_job(self):
    raise NotImplementedError()


  ##
  # Return the bassename of input filepath.
  #
  def __basename(self, filepath):
    return path.basename(filepath)


  ##
  #  Craft patform service full url path.
  #
  def _svc_url(self, svcUrlName):
    return self.connection_['protocol'] + '://' + self.connection_['ipaddr'] + \
        ':' + self.connection_['port'] + '/hop/' + svcUrlName

  ##
  #  @brief Load Platform application token by path.
  #  Currently, only one application token exists, giving access to all
  #  RAPP Platform Services!!
  #
  def load_app_token(self, app=""):
    ## TODO Load different tokens per application request.
    self.appToken_ = ''
    authParams = self.__read_json_file(path.join(self.cfgDir_, 'auth.json'))
    appTokenPath = path.expanduser(
        path.join(authParams['token_store_dir'], authParams['app_token']))

    with open(appTokenPath, 'r') as f:
      self.appToken_ = f.read()

  ##
  #
  #
  def __read_json_file(self, filepath):
    with open(filepath) as jsonData:
      data = json.load(jsonData)
      return data

  ##
  #  @brief Parse and load Rapp Platform parameters.
  #
  #  @param self The object pointer.
  #
  def __parse_platform_cfg(self):
    cfgFilePath = path.join(self.cfgDir_, 'platform.cfg')
    section = 'RAPP Platform'
    cfgParser = SafeConfigParser()

    try:
      cfgParser.read(cfgFilePath)
    except Exception as e:
      print "Could not load RAPP Platform parameters from .cfg file."
      print e
      sys.exit(1)
    if not cfgParser.has_section(section):
      print "\033[0mCfg file {%s} is missing section [%s]\033[0m" \
          % (cfgFilePath, section)
      sys.exit(1)

    if cfgParser.has_option(section, 'use'):
      useSection = cfgParser.get(section, 'use')
    else:
      print "Missing option under [RAPP Platform] section" + \
          " in cfg file {%s}" % cfgFilePath
      sys.exit(1)

    if not cfgParser.has_section(useSection):
      print "Given value for option <use> in [RAPP Platform] Section" + \
          " does not correspond to a defined Section in cfg file"
      sys.exit(1)

    if cfgParser.has_option(useSection, 'ipv4_addr') and \
        cfgParser.has_option(useSection, 'port'):
      self.connection_['ipaddr'] = cfgParser.get(useSection, 'ipv4_addr')
      self.connection_['port'] = cfgParser.get(useSection, 'port')
    else:
      print "Missing options {ipv4_addr} and {port} in cfg file [%s]" \
          % cfgFilePath
      sys.exit(1)
    if cfgParser.has_option(useSection, 'protocol'):
      self.connection_['protocol'] = cfgParser.get(useSection, 'protocol')
    else:
      print "Missing {protocol} option in platform cfg file." + \
          "Falling back to default {http}"
      self.connection_['protocol'] = 'http'


