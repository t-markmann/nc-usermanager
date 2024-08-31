#!/usr/bin/env python3
import os
import os.path
import sys
import time
import requests
import certifi
import csv
import string
import urllib.parse
import codecs
import html
import warnings
from tabulate import tabulate
from datetime import datetime
from bs4 import BeautifulSoup
from bs4.builder import XMLParsedAsHTMLWarning

warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

# This tool manages Nextcloud users (first features: disable/enable/delete users) from a CSV file, which you exported from some other software.

# Copyright (C) 2024 Torsten Markmann
# Mail: info@edudocs.de 
# WWW: edudocs.de

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

print("")
print("")
print("###################################################################################")
print("# NEXTCLOUD-USER-MANAGER                                                          #")
print("###################################################################################")
print("")
print("Copyright (C) 2024 Torsten Markmann (t-markmann), edudocs.de")
print("This program comes with ABSOLUTELY NO WARRANTY")
print("This is free software, and you are welcome to redistribute it under certain conditions.")
print("For details look into LICENSE file (GNU GPLv3).")
print("")

# Useful resources for contributors:
# Nextcloud user API https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_users.html
  # https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_users.html#delete-a-user
# Nextcloud group API https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_groups.html
# CURL to Python request converter https://curl.trillworks.com/

# determine if running in a build package (frozen) or from seperate python script
frozen = 'not'
if getattr(sys, 'frozen', False):
  # we are running in a bundle
  appdir = os.path.dirname(os.path.abspath(sys.executable))
  ## print("Executable is in frozen state, appdir set to: " + appdir) # for debug
else:
  # we are running in a normal Python environment
  appdir = os.path.dirname(os.path.abspath(__file__))
  ## print("Executable is run in normal Python environment, appdir set to: " + appdir) # for debug

# read config from xml file
configfile = codecs.open(os.path.join(appdir,'config.xml'),mode='r', encoding='utf-8')
config = configfile.read()
configfile.close()

# load config values into variables
config_xmlsoup = BeautifulSoup(config, "html.parser") # parse
config_ncUrl = config_xmlsoup.find('cloudurl').string
config_adminname = config_xmlsoup.find('adminname').string
config_adminpass = urllib.parse.quote(config_xmlsoup.find('adminpass').string)
config_action = config_xmlsoup.find('action').string
config_csvfile = config_xmlsoup.find('csvfile').string
config_csvDelimiter = config_xmlsoup.find('csvdelimiter').string
config_sslVerify = eval(config_xmlsoup.find('sslverify').string)


print("")
print("###################################################################################")
print("# Welcome to the Nextcloud user manager.                                          #")
print("# Please check the preview of the user list very carefully before you start       #")
print("# the process. We recommend to make a backup before deleting users.               #")
print("###################################################################################")
print("")
print("")
print("If you are sure that your settings in the config.xml are correct,")
print("press [ANY KEY] to continue.")
input("Otherwise, press [CONTROL + C] to abort the process.")
print("")
print("You have decided to continue. A user preview is generated.")
print("")    

# check if user-import-csv-filme exists
if not os.path.isfile(config_csvfile):
    print("ERROR!")
    print("The csv-file (" + config_csvfile + ") you specified in you config.xml does not exist. Please save '" + config_csvfile + "' in main-directory of the script or edit your config.xml")
    input("Press [ANY KEY] to confirm and end the process.")     
    sys.exit(1)

# cut http and https from ncUrl, because people often just copy & paste including protocol
config_ncUrl = config_ncUrl.replace("http://", "")
config_ncUrl = config_ncUrl.replace("https://", "")

# TODO optional: read config from input() if config.xml empty
# print('Username of creator (admin?):') 
# config_adminname = input()
# print('Password of creator:')
# config_adminpass = input()

config_protocol = "https" # use a secure connection!
config_apiUrl = "/ocs/v1.php/cloud/users" # nextcloud API path (users), might change in the future
config_apiUrlGroups = "/ocs/v1.php/cloud/groups" # nextcloud API path (groups), might change in the future

# Headers for CURL request, Nextcloud specific
requestheaders = {
  'OCS-APIRequest': 'true',
}

# set/create output-directory
output_dir = 'output'
if not os.path.exists(output_dir):
  os.makedirs(output_dir)

# adds date and time as string to variable
today = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') 


# display expected results before executing CURL
usertable = [["Username"]]
with codecs.open(os.path.join(appdir, config_csvfile),mode='r', encoding='utf-8') as csvfile:
  readCSV = csv.reader(csvfile, delimiter=config_csvDelimiter)
  next(readCSV, None)  # skip the headers
  for row in readCSV:
    if (len(row) != 1): # check if number of columns is consistent
      print("ERROR: row for user",html.escape(row[0]),"has",len(row),"columns. Should be 1. Please correct your csv-file.")
      input("Press [ANY KEY] to confirm and end the process.")
      sys.exit(1)
    line = html.escape(row[0])
    currentuser = [html.escape(row[0])]
    usertable.append(currentuser)
print(tabulate(usertable,headers="firstrow"))

# ask user to check values and continue
print("\nPlease check if the users above are as expected.")
print("\nYOUR PLANNED ACTION IS: " + config_action)
input("If everything is fine, press [ANY KEY] to continue. If not, press [CONTROL + C] to cancel.")
print("\nYou confirmed. I will now perform the planned actions. This can take a long time...\n")


# read rows from CSV file
with codecs.open(os.path.join(appdir, config_csvfile),mode='r', encoding='utf-8') as csvfile:
  readCSV = csv.reader(csvfile, delimiter=config_csvDelimiter)
  next(readCSV, None)  # skip the headers
  for row in readCSV:
    line = html.escape(row[0])

    print("Username:",html.escape(row[0]),)
    # build the dataset for the request
    data = [
      ('userid', html.escape(row[0]))
    ]

    if config_action == "disable":
      # perform the request for disable
      try:
        response = requests.put(config_protocol + '://' + config_adminname + ':' + config_adminpass + '@' + 
          config_ncUrl + config_apiUrl + "/" + html.escape(row[0]) + "/disable", headers=requestheaders, verify=config_sslVerify)
      except requests.exceptions.RequestException as e:  # handling errors
        print(e)
        print("The CURL request could not be performed.")
        input("Press [ANY KEY] to confirm and end the process.")
        sys.exit(1)
    elif config_action == "enable":
      # perform the request for enable
      try:
        response = requests.put(config_protocol + '://' + config_adminname + ':' + config_adminpass + '@' + 
          config_ncUrl + config_apiUrl + "/" + html.escape(row[0]) + "/enable", headers=requestheaders, verify=config_sslVerify)
      except requests.exceptions.RequestException as e:  # handling errors
        print(e)
        print("The CURL request could not be performed.")
        input("Press [ANY KEY] to confirm and end the process.")
        sys.exit(1)
    elif config_action == "delete":
      # perform the request for delete
      try:
        response = requests.delete(config_protocol + '://' + config_adminname + ':' + config_adminpass + '@' + 
          config_ncUrl + config_apiUrl + "/" + html.escape(row[0]), headers=requestheaders, verify=config_sslVerify)
      except requests.exceptions.RequestException as e:  # handling errors
        print(e)
        print("The CURL request could not be performed.")
        input("Press [ANY KEY] to confirm and end the process.")
        sys.exit(1)
    else: 
        print("Your planned action is not supported.")
        input("Press [ANY KEY] to confirm and end the process.")
        sys.exit(1)


    # catch wrong config
    if response.status_code != 200:
      print("HTTP Status: " + str(response.status_code))
      print("Your config.xml is wrong or your cloud is not reachable.")
      input("Press [ANY KEY] to confirm and end the process.")
      sys.exit(1)

    # show detailed info of response
    response_xmlsoup = BeautifulSoup(response.text, "html.parser")
    print(response_xmlsoup.find('status').string + ' ' + response_xmlsoup.find('statuscode').string + 
      ' = ' + response_xmlsoup.find('message').string)

    # append detailed response to logfile in output-folder
    logfile = codecs.open(os.path.join(output_dir,'output.log'),mode='a', encoding='utf-8')
    logfile.write("\nUSER: " + html.escape(row[0]) + "\nACTION: " + html.escape(config_action) + "\nTIME: " + time.strftime("%d.%m.%Y %H:%M:%S",time.localtime(time.time())) + 
      "\nRESPONSE: " + response_xmlsoup.find('status').string + ' ' + response_xmlsoup.find('statuscode').string + 
      ' = ' + response_xmlsoup.find('message').string + "\n")
    logfile.close()

print("")
print("###################################################################################")
print("# Control the status codes of the action above or in the output.log.              #")
print("# You should as well see the action in your Nextcloud now.                        #")
print("#                                                                                 #")
print("# For security reasons: please delete your credentials from config.xml            #")
print("###################################################################################")
print("")
input("Press [ANY KEY] to confirm and end the process.")
