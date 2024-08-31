# About nc-usermanager

This tool manages Nextcloud users from a CSV file, which you exported from some other software or created with a spreadsheet software.

Zip file with an executable for Windows is in the repository: click "code"--> "download zip" 

or: https://github.com/t-markmann/nc-usermanager/archive/refs/heads/main.zip

Unzip the file before executing the exe file. 

If you have a Python3 environment with all the dependencies/modules installed, you can run the script without the exe-build of course.

Screenshot:
![Screenshot from Windows commandline](https://github.com/t-markmann/nc-usermanager/blob/master/screenshot.png)

## Instructions

1. Download and extract the zip-file from https://get.edudocs.org/de/assets/nc-usermanager/

2. Insert data:
    * __config.xml__:
       * Insert your cloud-admin credentials into file _config.xml_. The user must have admin permissions in your Nextcloud.
       * Specify the action you want to perform for the users: *disable, enabled or delete*
    * __users.csv__: Insert the user data into the file _users.csv_ or recreate it with the same columns in a spreadsheet software.

3. Start the tool:
    * __Windows__: doubleclick _nc-usermanager.exe_.
    * __Linux__ / __Mac__: install all dependencies (https://github.com/t-markmann/nc-usermanager/wiki#install-dependencies-for-running-py-script) and run: python3 nc-usermanager.py
    	* __Troubleshooting__: Make sure the file is executable (https://www.qwant.com/?q=make%20file%20executable%20linux / https://www.qwant.com/?q=make%20file%20executable%20mac)

4. Follow the interactive commandline instructions. Check output.log ("output"-folder in script-directory) and your user overview in Nextcloud.


---

## ToDo

Open features, not yet implemented (help appreciated): 
* get list of users (and group memberships?) (https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_users.html#search-get-users --> empty search string?)
* apply action to all members of a defined group (https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_users.html#get-user-s-groups)
* ask if users exists first: https://docs.nextcloud.com/server/15/admin_manual/configuration_user/instruction_set_for_users.html
* manage group memberships?
