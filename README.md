# Download-Folder-Cleanup
https://github.com/Lesekater/Download-Folder-Cleanup

A script that cleans up PDF's in a folder by searching for them in google drive through the google drive api and uploading them if not available

## Description

### `downloadandcomare.py`
For a given directory, this script goes through the main folder and searches and compares every pdf-file by name with google drive. Based on the resuld it ether uploads or just moves the file to a newly generated "uploaded" folder.

---

## Installation

**Ubuntu**: A version of Python is already installed.  
**Mac OS X**: A version of Python is already installed. (SCRIPT IS NOT TESTED!!)  
**Windows**: You will need to install one of the 3.x versions available at [python.org](http://www.python.org/getit/). (SCRIPT IS NOT TESTED!!)  

## Dependencies
The script requires additional Python packages to run on the command line.

To install the Google client library for Python, run the following command:
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

To install python-magic follow the instructions on pypi.org:
https://pypi.org/project/python-magic/

To create credentials for a google api desktop application, follow the instructions given by google:
https://developers.google.com/workspace/guides/create-credentials

## General usage information

1. Download the script.
2. Install the Dependencies.
3. Run the script. (python3 downloadandcompare.py)

4. (optional). If this is your first time running the sample, the sample opens a new window prompting you to authorize access to your data:
    * If you are not already signed in to your Google account, you are prompted to sign in. If you are signed in to multiple Google accounts, you are asked to select one account to use for the authorization.
Note: Authorization information is stored on the file system, so subsequent executions don't prompt for authorization.
    * Click Accept. The app is authorized to access your data.
