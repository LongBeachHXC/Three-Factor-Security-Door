from data_model import UserObject, LogObject
from aws_handler import AwsHandler
from tkinter import *
from tkinter import ttk
import RPi.GPIO as GPIO

class DoorLockController(object):
	def __init__(self, db, view):
		self.db = db
		self.view = view
		self.aws_client = AwsHandler()
	
	def get_user_info(self, rfid_presented):
		query = { 'rfid_code' : f'{rfid_presented}'}
		return self.db.get_to_db('alist', query=query)
	
	def post_to_log(self, endpoint, payload):
		return self.db.post_new_doc(endpoint, payload)
	
	def update_access_log_doc(self, endpoint, object_id, payload):
		return self.db.update_doc(endpoint, object_id, payload)

	def retrieve_snapshot(self):
		return self.db.retrieve_snapshot_from_meraki()
	
	def user_db_image_url(self, endpoint, image_id):
		return self.db.get_image_url(endpoint, image_id)
	
	def compare_photos(self, source_image, target_image):
		return self.aws_client.comparePhotos(source_image, target_image)
	
	def initialize_gpio_board(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(13,GPIO.OUT)
	
	def door_contorl(self, flag):
		if flag == 'HIGH':
			GPIO.output(13,GPIO.HIGH)
		elif flag == 'LOW':
			GPIO.output(13,GPIO.LOW)
		else:
			print('Error...')

	def start(self):
		self.view.mainloop()
