#!/usr/bin/env python3
import sys
import os
import threading
import time
import RPi.GPIO as GPIO
import json
import requests
import asyncio
from threading import Thread
from random import randint
from queue import Queue
from evdev import InputDevice
from select import select
from door_lock_db import DoorLockDB
from aws_handler import AwsHandler
from tkinter import *
from tkinter import ttk
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

MERAKI_API_KEY = os.getenv('MERAKI_API_KEY')

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(13,GPIO.OUT)

db = DoorLockDB()
aws_client = AwsHandler()

access_log_id = str()
pin = str()

class MerakiApiCall(Thread):
	
	def __init__(self, *args, **kwargs):
		super().__init__()

	def run(self):
		self.result = None
		# self.result = self.db.retrieve_snapshot_from_meraki()
		url = 'https://api.meraki.com/api/v0/networks/N_605734149881365386/cameras/Q2HV-9HKP-5FDR/snapshot'
		headers = {
			'X-Cisco-Meraki-API-Key' : MERAKI_API_KEY
		}
		snapshot_url_request = requests.request('POST', url, headers=headers)
		snapshot_url_json = snapshot_url_request.json()
		self.result = snapshot_url_json['url']
		# return(snapshot_url)
class Fullscreen_Window:
	
	def __init__(self):
		self.tk = Tk()
		self.tk.title("Three-Factor Authentication Security Door Lock")
		self.frame = Frame(self.tk)
		self.frame.grid()
		self.tk.columnconfigure(0, weight=1)
		self.tk.columnconfigure(1, weight=1)
		self.tk.columnconfigure(2, weight=1)
		self.tk.columnconfigure(3, weight=1)
		self.remaining = 0
		self.meraki_url = ''
		self.meraki_thread = None
		
		self.tk.attributes('-zoomed', True)
		self.tk.attributes('-fullscreen', True)
		# self.state = True
		self.tk.bind("<F11>", self.toggle_fullscreen)
		self.tk.bind("<Escape>", self.end_fullscreen)
		self.tk.config(cursor="none")
		self.PINentrytimeout = None
		
		self.show_idle()
		
		t = Thread(target=self.listen_rfid)
		t.daemon = True
		t.start()

	# def check_queue(self):
	# 	if not self.queue.empty():
	# 		self.meraki_url = self.queue.get()
	# 	else:
	# 		self.tk.after(100, self.check_queue)

	def check_thread(self, thread):
		print(thread)
		if thread is not None:
			if thread.is_alive():
				self.tk.after(100, lambda: self.check_thread(thread))
			else:	
				self.meraki_url = thread.result
				print(self.meraki_url)
		else:
			self.tk.after(100, lambda: self.check_thread(thread))
	
	def meraki_api_thread(self):
		self.meraki_thread = MerakiApiCall()
		self.meraki_thread.start()

	def show_idle(self):
		self.welcomeLabel = ttk.Label(self.tk, text="Please Present\nYour Token")
		self.welcomeLabel.config(font='size, 20', justify='center', anchor='center')
		self.welcomeLabel.grid(columnspan=3, padx=125, pady=125)
	
	def pin_entry_forget(self):
		self.validUser.grid_forget()
		self.photoLabel.grid_forget()
		self.enterPINlabel.grid_forget()
		count = 0
		while (count < 12):
			self.btn[count].grid_forget()
			count += 1
		self.tk.update
	
	def pin_result_forget(self):
		self.PINresultLabel.grid_forget()
		self.countdownTimerLabel.grid_forget()

	def face_match_forget(self):
		self.face_match_label.grid_forget()

	def retruntoIdle_from_snapshot_fail(self):
		self.face_match_forget()
		self.show_idle()
		
	def returnToIdle_fromPINentry(self):
		self.pin_entry_forget()
		self.pin_result_forget()
		self.show_idle()
		
	def returnToIdle_fromPINentered(self):
		self.pin_entry_forget()
		self.pin_result_forget()
		self.show_idle()
		
	def returnToIdle_fromAccessGranted(self):
		GPIO.output(13,GPIO.LOW)
		# self.SMSresultLabel.grid_forget()
		# self.returnToIdle_fromPINentered()
		self.face_match_forget()
		self.show_idle()
		

	def returnToIdle_fromFaceMatchFail(self):
		self.face_match_forget()
		self.show_idle()
	# def returnToIdle_fromSMSentry(self):
	# 	self.PINresultLabel.grid_forget()
	# 	self.smsDigitsLabel.grid_forget()
	# 	count = 0
	# 	while (count < 12):
	# 		self.btn[count].grid_forget()
	# 		count += 1
	# 	self.show_idle()
		
	# def	returnToIdle_fromSMSentered(self):
	# 	self.SMSresultLabel.grid_forget()
	# 	self.show_idle()
	
	def toggle_fullscreen(self, event=None):
		self.state = not self.state  # Just toggling the boolean
		self.tk.attributes("-fullscreen", self.state)
		return "break"

	def end_fullscreen(self, event=None):
		self.state = False
		self.tk.attributes("-fullscreen", False)
		return "break"

	# def api_call_to_meraki(self):
	# 	meraki_base_uri = 'https://api.meraki.com/api/v0/networks/N_605734149881365386/cameras/Q2HV-9HKP-5FDR/snapshot'
	# 	headers = {
	# 		'X-Cisco-Meraki-API-Key' : MERAKI_API_KEY
	# 	}
	# 	snapshot_url_request = requests.request('POST', meraki_base_uri, headers=headers)
	# 	snapshot_url_json = snapshot_url_request.json()
	# 	snapshot_url = snapshot_url_json['url']
	# 	return(snapshot_url)

	# def user_db_image(self, user_image_id):
	# 	url = db.get_image_url('m', user_image_id)
	# 	image = requests.request('GET', url)
	# 	return(image.content)
	

	def countdown(self):
		'''start countdown 10 seconds before new year starts'''
		for k in range(5, 0, -1):
			self.countdownTimerLabel["text"] = k
			self.tk.update()
			time.sleep(1)
		self.countdownTimerLabel["text"] = "Picture Taken"
		self.tk.update()
		# self.meraki_api_thread()
		return db.retrieve_snapshot_from_meraki()


	# def countdown(self, remaining=None):
	# 	if remaining is not None:
	# 		self.remaining = remaining
		
	# 	if self.remaining <= 0:
	# 		self.countdownTimerLabel.configure(text="Picture Taken")
	# 		self.meraki_api_thread()
	# 	else:
	# 		self.countdownTimerLabel.configure(text="%d" % self.remaining)
	# 		self.remaining = self.remaining - 1
	# 		self.tk.after(1000, lambda: self.countdown)
	# 		return False
		
	
	# def asyncio_thread(event_loop):
	# 	print('The tasks of fetching multiple URLs begins')
	# 	event_loop.run_until_complete(simulate_fetch_all_urls())

	# def execute_tasks_in_a_new_thread(event_loop):
	# 	""" Button-Event-Handler starting the asyncio part. """
	# 	Thread(target=asyncio_thread, args=(event_loop, )).start()
	
	# async def simulate_fetch_one_url(url):
	# 	""" We simulate fetching of URL by sleeping for a random time """
	# 	seconds = random.randint(1, 8)
	# 	await asyncio.sleep(seconds)
	# 	return 'url: {}\t fetched in {} seconds'.format(url, seconds)
	

	
	def listen_rfid(self):
		global pin
		global access_log_id
		
		keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
		dev = InputDevice('/dev/input/event0')
		rfid_presented = ""

		while True:
			r,w,x = select([dev], [], [])
			for event in dev.read():
				if event.type==1 and event.value==1:
						if event.code==28:
							# dbConnection = MySQLdb.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbName)
							# cur = dbConnection.cursor(MySQLdb.cursors.DictCursor)
							# cur.execute("SELECT * FROM access_list WHERE rfid_code = '%s'" % (rfid_presented))
							query = { 'rfid_code' : f'{rfid_presented}'}
							rfid_user = db.get_to_db('alist', query=query)
							
							if len(rfid_user) != 1:
								self.welcomeLabel.config(text="ACCESS DENIED", justify='center', anchor='center')
								
								# Log access attempt
								# cur.execute("INSERT INTO access_log SET rfid_presented = '%s', rfid_presented_datetime = NOW(), rfid_granted = 0" % (rfid_presented))
								# dbConnection.commit()
								localtime = time.asctime( time.localtime(time.time()) )
								payload = {
									'rfid_presented' : f'{rfid_presented}',
									'rfid_presented_datetime' : f'{localtime}',
									'rfid_granted' : 0
								}
								time.sleep(3)
								self.welcomeLabel.grid_forget()
								self.show_idle()
							else:
								print(rfid_user)
								user_info = rfid_user[0]
								userPin = str(user_info['pin'])
								image_url = user_info['image']
								self.welcomeLabel.grid_forget()
								self.validUser = ttk.Label(self.tk, text=f"Welcome\n {user_info['name']}!", font='size, 15', justify='center', anchor='center')
								self.validUser.grid(columnspan=3, sticky=W+E)
								self.image = PhotoImage(file='image75.gif')
								self.photoLabel = ttk.Label(self.tk, image=self.image, justify='center', anchor='center')
								self.photoLabel.grid(columnspan=3, sticky=W+E)
								
								self.enterPINlabel = ttk.Label(self.tk, text='Please enter your PIN:', font='size, 18', justify='center', anchor='center')
								self.enterPINlabel.grid(columnspan=3, sticky=W+E)
								pin = ''
								
								keypad = [
									'1', '2', '3',
									'4', '5', '6',
									'7', '8', '9',
									'*', '0', '#',
								]
								
								# create and position all buttons with a for-loop
								# r, c used for row, column grid values
								r = 4
								c = 0
								n = 0
								# list(range()) needed for Python3
								self.btn = list(range(len(keypad)))
								print('----- we got here ------')
								for label in keypad:
									# partial takes care of function and argument
									#cmd = partial(click, label)
									# create the button
									self.btn[n] = Button(self.tk, text=label, font='size, 16', width=4, height=1, command=lambda digitPressed=label:self.codeInput(digitPressed, userPin, image_url))
									# position the button
									self.btn[n].grid(row=r, column=c, padx=15, ipady=0)
									# increment button index
									n += 1
									# update row/column position
									c += 1
									if c > 2:
										c = 0
										r += 1
									
								print('--------- *** -----')
								
								# Log access attempt
								# cur.execute("INSERT INTO access_log SET rfid_presented = '%s', rfid_presented_datetime = NOW(), rfid_granted = 1" % (rfid_presented))
								# dbConnection.commit()
								localtime = time.asctime( time.localtime(time.time()) )
								payload = {
									'rfid_presented' : f'{rfid_presented}',
									'rfid_presented_datetime' : f'{localtime}',
									'rfid_granted' : 1
								}
								try:
									rfid_log = db.post_new_doc('alog', payload)
									access_log_id = rfid_log['_id']
								except Exception as e:
									print(e)
							
								self.PINentrytimeout = threading.Timer(10, self.returnToIdle_fromPINentry)
								self.PINentrytimeout.daemon = True
								self.PINentrytimeout.start()
								
								
								self.PINenteredtimeout = threading.Timer(5, self.returnToIdle_fromPINentered)
								self.PINenteredtimeout.daemon = True
							
							rfid_presented = ""
							# dbConnection.close()
						else:
							rfid_presented += keys[ event.code ]
							print(rfid_presented)

	def codeInput(self, value, userPin, user_image_id):
		global access_log_id
		global pin
		pin += value
		pinLength = len(pin)
		
		self.enterPINlabel.config(text=f'Digits Entered: {pinLength}')
		print('we got here ----', self.PINentrytimeout)
		
		if pinLength == 4:
			if self.PINentrytimeout:
				self.PINentrytimeout.cancel()
			self.pin_entry_forget()
			
			if pin == userPin:
				pin_granted = 1
			else:
				pin_granted = 0
			
			# Log access attempt
			# dbConnection = MySQLdb.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbName)
			# cur = dbConnection.cursor()
			# cur.execute("UPDATE access_log SET pin_entered = '%s', pin_entered_datetime = NOW(), pin_granted = %s, mobile_number = '%s' WHERE access_id = %s" % (pin, pin_granted, mobileNumber, accessLogId))
			# dbConnection.commit()
			localtime = time.asctime( time.localtime(time.time()) )
			payload = {
				'pin_entered' : f'{pin}',
				'pin_entered_datetime' : f'{localtime}',
				'pin_granted' : f'{pin_granted}'
			}
			try:
				doc = db.update_doc('alog', access_log_id, payload)
			except Exception as e:
				print(e)

			# print(f'This is the pin: {pin}')
			# print(f'This is the db pin: {userPin}')
			if pin == userPin:
				# self.PINresultLabel = ttk.Label(self.tk, text="Thank You, Please Press\nThe Button To\nTake Picture")
				# self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
				# self.PINresultLabel.grid(columnspan=3, sticky=W+E+N+S, pady=50)

				# self.pin_result_button = Button(self.tk, text='Take Photo', font='size, 16', width=4, height=1, command=lambda :self.face_match_flow(user_image_id))
				# # self.pin_result_button.config(font='size, 20', justify='center', anchor='center')
				# self.pin_result_button.grid(columnspan=3)
				self.PINresultLabel = ttk.Label(self.tk, text="Thank You, Please Look\nAt The Camera")
				self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
				self.PINresultLabel.grid(columnspan=3, sticky=W+E+N+S, pady=50)

				

				# # self.facialRecognitionTimerButton = Button(self.tk, text='Start', font='size, 16', width=4, height=1, command=awsFacialCompare)
				self.countdownTimerLabel = ttk.Label(self.tk, text='5', width=10)
				self.countdownTimerLabel.config(font='size, 36', justify='center', anchor='center')
				self.countdownTimerLabel.grid(columnspan=3, sticky=W+E)

				self.meraki_url = self.countdown()
				# time.sleep(8)
				# self.check_thread(self.meraki_thread)
				# self.meraki_api_thread()
				print(self.meraki_url, '<<<<<<<<<<<<<<<')

				self.pin_result_forget()

				self.face_match_label = ttk.Label(self.tk, text='')
				self.face_match_label.config(font='size, 30', justify='center', anchor='center')
				self.face_match_label.grid(columnspan=3, sticky=W+E, pady=125)
				
				if self.meraki_url:
					user_db_photo =  db.get_image_url('m', user_image_id)
					self.face_match_label['text'] = 'Comparing photo...'
					self.tk.update()
					face_match = aws_client.comparePhotos(user_db_photo, self.meraki_url)
					if face_match:
						self.face_match_label['text'] = 'Match!'
						self.tk.update()
						GPIO.output(13,GPIO.HIGH)
						self.doorOpenTimeout = threading.Timer(10, self.returnToIdle_fromAccessGranted)
						self.doorOpenTimeout.daemon = True
						self.doorOpenTimeout.start()
					else:
						self.face_match_label['text'] = 'No Match'
						self.tk.update()
						self.face_match_fail = threading.Timer(10, self.returnToIdle_fromFaceMatchFail)
						self.face_match_fail.daemon = True
						self.face_match_fail.start()
				else:
					self.face_match_label['text'] = 'Error...'
					self.tk.update()
					self.snapshot_fail = threading.Timer(5, self.retruntoIdle_from_snapshot_fail)
					self.snapshot_fail.daemon = True
					self.snapshot_fail.start()
				# self.meraki_api_thread(db)
				# for k in range(5, 0, -1):
				# 	self.countdownTimerLabel["text"] = k
				# 	self.tk.update()
				# 	time.sleep(1)
				# self.countdownTimerLabel["text"] = "Picture Taken"
				# self.tk.update()
				# rturn = db.retrieve_snapshot_from_meraki()
				# time.sleep(5)


				# snap_img_src = self.door_snapshot(image_url)
				# user_db_img_src = self.user_db_image(user_image_id)
				# print(type(snap_img_src))
				# print(type(user_db_img_src))
				# if commp(img_src, img_db):
				#    tru
				# else:
				#   False
			else:
				# self.PINresultLabel.grid_forget()
				self.PINresultLabel = ttk.Label(self.tk, text="Incorrect PIN\nEntered!")
				self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
				self.PINresultLabel.grid(columnspan=3, sticky=W+E+N+S, pady=125)
				self.PINenteredtimeout.start()
	
	# def face_match_flow(self, user_image_id):
		
	# 	self.PINresultLabel.grid_forget()
	# 	self.pin_result_button.grid_forget()

	# 	self.face_match_label = ttk.Label(self.tk, text='Photo Taken')
	# 	self.face_match_label.config(font='size, 30', justify='center', anchor='center')
	# 	self.face_match_label.grid(columnspan=3, sticky=W+E, pady=125)

	# 	self.meraki_url = db.retrieve_snapshot_from_meraki()
	# 	# self.check_thread(self.meraki_thread)
	# 	# self.meraki_api_thread()
	# 	print(self.meraki_url, '<<<<<<<<<<<<<<<')
		
	# 	if self.meraki_url:
	# 		user_db_photo =  db.get_image_url('m', user_image_id)
	# 		self.face_match_label['text'] = 'Comparing photo...'
	# 		self.tk.update()
	# 		face_match = aws_client.comparePhotos(user_db_photo, self.meraki_url)
	# 		if face_match:
	# 			self.face_match_label['text'] = 'Match!'
	# 			self.tk.update()
	# 			GPIO.output(13,GPIO.HIGH)
	# 			self.doorOpenTimeout = threading.Timer(10, self.returnToIdle_fromAccessGranted)
	# 			self.doorOpenTimeout.daemon = True
	# 			self.doorOpenTimeout.start()
	# 		else:
	# 			self.face_match_label['text'] = 'No Match'
	# 			self.tk.update()
	# 			self.face_match_fail = threading.Timer(10, self.returnToIdle_fromFaceMatchFail)
	# 			self.face_match_fail.daemon = True
	# 			self.face_match_fail.start()
	# 	else:
	# 		self.face_match_label['text'] = 'Error...'
	# 		self.tk.update()
	# 		self.snapshot_fail = threading.Timer(5, self.retruntoIdle_from_snapshot_fail)
	# 		self.snapshot_fail.daemon = True
	# 		self.snapshot_fail.start()
	# 	pass
	# def awsFacialCompare(self, image)				
	# def smsCodeEnteredInput(self, value, smsCode):
	# 	global smsCodeEntered
	# 	global accessLogId
	# 	smsCodeEntered += value
	# 	smsCodeEnteredLength = len(smsCodeEntered)
		
	# 	self.smsDigitsLabel.config(text="Digits Entered: %d" % smsCodeEnteredLength)
		
	# 	if smsCodeEnteredLength == 6:
	# 		self.SMSentrytimeout.cancel()
	# 		self.pin_entry_forget()
			
	# 		if smsCodeEntered == smsCode:
	# 			smscode_granted = 1
	# 		else:
	# 			smscode_granted = 0
			
	# 		# Log access attempt
	# 		dbConnection = MySQLdb.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbName)
	# 		cur = dbConnection.cursor()
	# 		cur.execute("UPDATE access_log SET smscode_entered = '%s', smscode_entered_datetime = NOW(), smscode_granted = %s WHERE access_id = %s" % (smsCodeEntered, smscode_granted, accessLogId))
	# 		dbConnection.commit()
			
			# if smsCodeEntered == smsCode:
			# 	self.SMSresultLabel = ttk.Label(self.tk, text="Thank You,\nAccess Granted")
			# 	self.SMSresultLabel.config(font='size, 20', justify='center', anchor='center')
			# 	self.SMSresultLabel.grid(columnspan=3, sticky=tk.W+tk.E, pady=210)
				
			# 	self.PINresultLabel.grid_forget()
			# 	self.smsDigitsLabel.grid_forget()
			# 	GPIO.output(13,GPIO.HIGH)
				
			# 	self.doorOpenTimeout = threading.Timer(10, self.returnToIdle_fromAccessGranted)
			# 	self.doorOpenTimeout.start()
			# else:
			# 	self.PINresultLabel.grid_forget()
			# 	self.smsDigitsLabel.grid_forget()
				
			# 	self.SMSresultLabel = ttk.Label(self.tk, text="Incorrect SMS\nCode Entered!")
			# 	self.SMSresultLabel.config(font='size, 20', justify='center', anchor='center')
			# 	self.SMSresultLabel.grid(sticky=tk.W+tk.E, pady=210)
				
			# 	self.SMSenteredtimeout = threading.Timer(10, self.returnToIdle_fromSMSentered)
			# 	self.SMSenteredtimeout.start()
				
	# def sendSMScode(self, mobileNumber):
	
	# 	# Retreive our Twilio access credentials and "from" number
	# 	dbConnection = MySQLdb.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbName)
	# 	cur = dbConnection.cursor(MySQLdb.cursors.DictCursor)
	# 	cur.execute("SELECT account_sid, auth_token, twilio_sms_number FROM twilio_api_credentials WHERE id = 1")
	# 	credentials = cur.fetchone()
	# 	account_sid = credentials['account_sid']
	# 	auth_token = credentials['auth_token']
	# 	twilio_sms_number = credentials['twilio_sms_number']
	# 	dbConnection.close()
				
	# 	smsCode = str(randint(100000, 999999))
	# 	messageText = "Your access code is %s. Please enter this on the touchscreen to continue." % smsCode

	# 	client = Client(account_sid, auth_token)
	# 	message = client.messages.create(
	# 		to=mobileNumber, 
	# 		from_=twilio_sms_number,
	# 		body=messageText)
		
	# 	return smsCode

if __name__ == '__main__':
	w = Fullscreen_Window()
	w.tk.mainloop()