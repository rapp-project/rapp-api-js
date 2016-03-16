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
from requests.auth import HTTPBasicAuth  # Http basic authentication
from requests.exceptions import *  # Requests Exceptions
from ServiceControllerBase import *
from RAPPAuth import RAPPAuth
import json
import time


## @class CloudInterface
#
#  Cloud Interface class. Service controller for HOP Web Services requests
#  Static class.
#
class ServiceControllerSync(ServiceControllerBase):

  def __init__(self, connect, timeout=None, token="", \
          persistent_connection=True):
    self.timeout_ = timeout
    super(ServiceControllerSync, self).__init__()

    self.connection['ipaddr'] = connect['ipaddr']
    self.connection['port'] = connect['port']
    self.connection['protocol'] = connect['protocol']
    self.token_ = token
    self.persistentConn_ = persistent_connection
    if self.persistentConn_:
        # Initialize the Session object to be used for the http
        #  persistent connection
        self.__http_persistent_connection()


  ## Performs Platform's HOP Web Service request.
  #
  #   @param basicAuth Basic http authentication credentials
  #       {'username': '', 'password': ''}
  #   @param url Post request destination Url.
  #   @param payload data payload of the post request.
  #   @param files multipart post file field.
  #
  #   @return Rapp Platform Service response object.
  #
  def run_job(self, svcUrlName, payload, files):
    #  Python-Requests module does not support empty parameter fields.
    #  Passing empty parameter ('param1': '') will result in a corrupted
    #  payload definition.
    #  Referenced issue on github:
    #      https://github.com/kennethreitz/requests/issues/2651
    #  Below we provide a temporary fix to this issue.
    #      Deleting values from payload literal does the job!

    multiFiles = []
    for f in files:
      fTuple = self._make_file_tuple(f['path'], f['field_name'])
      multiFiles.append(fTuple)

    toRemove = []
    for param in payload:
      if not payload[param]:
        toRemove.append(param)
    for i in toRemove:
      del payload[i]

    url = self._svc_url(svcUrlName)
    if self.persistentConn_:
        resp = self.__post_persistent(url, payload, multiFiles)
    else:
        resp = self.__post_session_once(url, payload, multiFiles)
    return resp


  ##
  #  @brief Create instance Session Object. The Session object is stored
  #   as a member variable. Used to perform http persistent connections
  #   connection: 'heep-alive'
  ##
  def __http_persistent_connection(self):
    self.session_ = requests.Session()



  ##
  #  @brief General member method to perform a .post request to the
  #    Platform service.
  #    If files are specified, then multipart/form-data form is used.
  #    Otherwhise, x-www-urlencoded form is used.
  #
  #  @param session The session oject to use for this request.
  #  @param urlpath The complete urlpath of the request.
  #  @param data The data to send. Literal.
  #  @param files Files to send.
  #
  def post_request(self, session, urlpath, data={}, files=[]):
    # payload = self._make_payload_dic(data)
    payload = data
    try:
        resp = session.post(url=urlpath, data=payload, files=files, \
          timeout=self.timeout_, verify=False, auth=RAPPAuth(self.token_))
    except RequestException as e:
      errorMsg = self.handle_exception(e)
      resp = {
          'error': errorMsg
      }
    else:
      if self.is_json(resp.content):
        resp = json.loads(resp.content)
      else:
        resp = {
          'payload': resp.content,
          'error': 'Non application/json response'
        }
    return resp


  def __post_session_once(self, urlpath, data, files):
    with requests.Session() as session:
      resp = self.post_request(session, urlpath, data, files)
    return resp


  def __post_persistent(self, urlpath, data, files):
    return self.post_request(self.session_, urlpath, data, files)


  ##
  #  @brief Load Platform application token by path.
  #  @TODO
  ##
  def __load_token(self, tokenpath):
    pass


  ##
  #  @brief handles exceptions and return an error message that complies to the
  #   Exception caught.
  #
  #  @param exc Exception
  ##
  def handle_exception(self, exc):
    print type(exc)
    errorMsg = ''
    if type(exc) is ConnectionError:
      errorMsg = "Connection Error"
    elif type(exc) is HTTPError:
      errorMsg = "An HTTP error occured"
    elif type(exc) is ConnectTimeout:
      errorMsg = "The request timed out while trying to connect to the remote server"
    elif type(exc) is ReadTimeout:
      errorMsg = "The server did not send any data in the allotted amount of time."
    elif type(exc) is Timeout:
      errorMsg = "Connection Timeout exception."
    else:
      errorMsg = "Catched Exception %s" %exc

    return errorMsg