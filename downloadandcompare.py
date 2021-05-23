# import the required libraries
from __future__ import print_function
import pickle
import os.path
import io
import shutil
import requests
import filecmp
import os
import magic
from mimetypes import MimeTypes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload

mime_pdf = "application/pdf"

class DriveAPI:
	
	# define the scopes
	SCOPES = ['https://www.googleapis.com/auth/drive']

	def __init__(self):
		
		# Variable self.creds will
		# store the user access token.
		# If no valid token found
		# we will create one.
		self.creds = None

		# The file token.pickle stores the
		# user's access and refresh tokens. It is
		# created automatically when the authorization
		# flow completes for the first time.

		# Check if file token.pickle exists
		creds_file = 'token.pickle'
		if os.path.exists(creds_file):

			# Read the token from the file and
			# store it in the variable self.creds
			with open(creds_file, 'rb') as token:
				self.creds = pickle.load(token)

		# If no valid credentials are available,
		# request the user to log in.
		if not self.creds or not self.creds.valid:

			# If token is expired, it will be refreshed,
			# else, we will request a new one.
			if self.creds and self.creds.expired and self.creds.refresh_token:
				self.creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
					'credentials.json', self.SCOPES)
				self.creds = flow.run_local_server(port=0)

			# Save the access token in token.pickle
			# file for future usage
			with open(creds_file, 'wb') as token:
				pickle.dump(self.creds, token)

		# Connect to the API service
		self.service = build('drive', 'v3', credentials=self.creds)

	# downloads pdf file with file-id
	# OR Exports and downloads google docs file with file-id 
	# and compares with local file
	# return [comparison result, error state]
	def download_and_compare(self, file_id, file_dest, cleaning_directory, file_type):
		if file_type == mime_pdf:
			request = self.service.files().get_media(fileId=file_id)
		elif file_type == "application/vnd.google-apps.document":
			request = self.service.files().export_media(fileId=file_id, mimeType=mime_pdf)
		else:
			return [False, False]
		fh = io.BytesIO()
		tmpfile = cleaning_directory + "tmpfile.pdf"
		
		# Initialise a downloader object to download the file
		downloader = MediaIoBaseDownload(fh, request)
		done = False

		try:
			# Download the data in chunks
			while not done:
				status, done = downloader.next_chunk()
			fh.seek(0)
			
			# Write the received data to the file
			with open(tmpfile, 'wb') as f:
				shutil.copyfileobj(fh, f)
			
			#compare files
			comparison_result = filecmp.cmp(tmpfile, file_dest)

			if os.path.exists(tmpfile):
  				os.remove(tmpfile)

			# return [True, error State] if file comarison was successfully
			return [comparison_result, True]
		except:
			# return [False, False] if something went wrong
			print("Something went wrong.")
			return [False, False]

	# finds file on drive
	# return [file-id's]
	def find_file(self, filename):
		file_list = []

		page_token = None
		while True:
			response = self.service.files().list(q=("name contains '"+(os.path.splitext(filename)[0])+"'"),
												spaces='drive',
												fields='nextPageToken, files(id, name, mimeType)',
												pageToken=page_token).execute()
			for file in response.get('files', []):
				# Process change
				print('Found file: %s (%s) , %s' % (file.get('name'), file.get('id'), file.get('mimeType')))
				file_list.append([file.get('id'), file.get('mimeType')])
			page_token = response.get('nextPageToken', None)
			if page_token is None:
				break
		return file_list

	# uploads file with file destination and filename
	# return nothing
	def upload_file(self, file_dest, filename):
		file_metadata = {
			"name": filename,
			"parents": "root"
		}
		media = MediaFileUpload(filename, resumable=True)
		file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
		print("File created, id:", file.get("id"))

	# checks if file is already on drive with cleaning_directory and filename
	# returns outcome (true/ false)
	def check_type_and_compare(self, cleaning_directory, filename):
		#check for file in Drive
		is_file_in_drive = obj.find_file(filename)
		#filename is found in drive
		for current_file in is_file_in_drive:
			#file is pdf or google doc
			result = obj.download_and_compare(current_file[0], (cleaning_directory + filename), cleaning_directory, current_file[1])
			if not result[1]:
				break
			#file is similar to the file in drive
			elif result[0] and result[1]:
				os.rename(cleaning_directory + filename, cleaning_directory + "uploaded/" + filename)
				return True
		return False


if __name__ == "__main__":
	obj = DriveAPI()
	#detect current directory
	cleaningDirectory = os.path.dirname(os.path.realpath(__file__)) + "/"
	#check for upload folder and create if missing
	if not os.path.exists(cleaningDirectory + "/uploaded"):
		os.mkdir(cleaningDirectory + "/uploaded")

	#Go throught Folder
	f = []
	for (dirpath, dirname, filename) in os.walk(cleaningDirectory):
		f.extend(filename)
		break

	#compare files with drive
	for filename in f:
		print(filename)
		#check if file is of type pdf
		mime = magic.Magic(mime=True)
		#search for file in drive
		if(mime.from_file(cleaningDirectory + filename) == mime_pdf) and not obj.check_type_and_compare(cleaningDirectory, filename):
			#filename not found in drive or not similar to the file
			obj.upload_file(cleaningDirectory, filename)
			os.rename(cleaningDirectory + filename, cleaningDirectory + "uploaded/" + filename)