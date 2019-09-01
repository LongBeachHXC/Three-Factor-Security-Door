#!/usr/bin/env python3
import sys
from threading import Thread
import threading
import time
import RPi.GPIO as GPIO
import json
from random import randint
from evdev import InputDevice
from select import select
from door_lock_db import DoorLockDB
from tkinter import *
from tkinter import ttk

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(5,GPIO.OUT)

db = DoorLockDB()

accessLogId = str()
pin = str()

class Fullscreen_Window:
	
	def __init__(self):
		self.tk = Tk()
		self.tk.title("Three-Factor Authentication Security Door Lock")
		self.frame = Frame(self.tk)
		self.frame.grid()
		self.tk.columnconfigure(0, weight=1)
		
		self.tk.attributes('-zoomed', True)
		self.tk.attributes('-fullscreen', True)
		self.state = True
		self.tk.bind("<F11>", self.toggle_fullscreen)
		self.tk.bind("<Escape>", self.end_fullscreen)
		self.tk.config(cursor="none")

		self.db = DoorLockDB()
		
		self.show_idle()
		
		t = Thread(target=self.listen_rfid)
		t.daemon = True
		t.start()
		
	def show_idle(self):
		self.welcomeLabel = ttk.Label(self.tk, text="Please Present\nYour Token")
		self.welcomeLabel.config(font='size, 20', justify='center', anchor='center')
		self.welcomeLabel.grid(pady=150)
	
	def pin_entry_forget(self):
		self.validUser.grid_forget()
		self.photoLabel.grid_forget()
		self.enterPINlabel.grid_forget()
		count = 0
		while (count < 12):
			self.btn[count].grid_forget()
			count += 1
		
	def returnToIdle_fromPINentry(self):
		self.pin_entry_forget()
		self.show_idle()
		
	def returnToIdle_fromPINentered(self):
		self.PINresultLabel.grid_forget()
		self.show_idle()
		
	def returnToIdle_fromAccessGranted(self):
		GPIO.output(5,GPIO.LOW)
		self.SMSresultLabel.grid_forget()
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
		
	def listen_rfid(self):
		global pin
		global accessLogId
		
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
							rfid_user = self.db.get_to_db('alist', query=query)
							
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
								db.post_new_doc('alog', payload)
								time.sleep(3)
								self.welcomeLabel.grid_forget()
								self.show_idle()
							else:
								user_info = rfid_user[0]
								userPin = user_info['pin']
								self.welcomeLabel.grid_forget()
								self.validUser = ttk.Label(self.tk, text=f"Welcome\n {user_info['name']}!", font='size, 15', justify='center', anchor='center')
								self.validUser.grid(columnspan=3, sticky=W+E+N+S)
								self.image = PhotoImage(file='resize150.gif')
								self.photoLabel = ttk.Label(self.tk, image=self.image)
								self.photoLabel.grid(columnspan=3, sticky=W+E+N+S)
								
								self.enterPINlabel = ttk.Label(self.tk, text='Please enter your PIN:', font='size, 18', justify='center', anchor='center')
								self.enterPINlabel.grid(columnspan=3, sticky=W+E+N+S)
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
								for label in keypad:
									# partial takes care of function and argument
									#cmd = partial(click, label)
									# create the button
									self.btn[n] = Button(self.tk, text=label, font='size, 16', width=2, height=1, command=lambda digitPressed=label:self.codeInput(digitPressed, userPin))
									# position the button
									self.btn[n].grid(row=r, column=c, ipadx=0, ipady=0)
									# increment button index
									n += 1
									# update row/column position
									c += 1
									if c > 2:
										c = 0
										r += 1

								
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
									access_log_entry = db.post_new_doc('alog', payload)
									accessLogId = access_log_entry['access_id']
								except Exception as e:
									print(e)
							
								self.PINentrytimeout = threading.Timer(10, self.returnToIdle_fromPINentry)
								self.PINentrytimeout.start()
								
								self.PINenteredtimeout = threading.Timer(5, self.returnToIdle_fromPINentered)
							
							rfid_presented = ""
							# dbConnection.close()
						else:
							rfid_presented += keys[ event.code ]
							print(rfid_presented)

	def codeInput(self, value, userPin):
		global accessLogId
		global pin
		pin += value
		pinLength = len(pin)
		
		self.enterPINlabel.config(text=f'Digits Entered: {pinLength}')
		
		if pinLength == 4:
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
				db.post_new_doc('alog', payload)
			except Exception as e:
				print(e)

			if pin == userPin:
				self.PINresultLabel = ttk.Label(self.tk, text="Thank You,\nAccess Granted")
				self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
				self.PINresultLabel.grid(columnspan=3, sticky=W+E+N+S, pady=210)
				
				self.PINresultLabel.grid_forget()
				# self.smsDigitsLabel.grid_forget()
				GPIO.output(13,GPIO.HIGH)
				
				self.doorOpenTimeout = threading.Timer(10, self.returnToIdle_fromAccessGranted)
				self.doorOpenTimeout.start()
			else:
				# self.PINresultLabel.grid_forget()
				self.PINresultLabel = ttk.Label(self.tk, text="Incorrect PIN\nEntered!")
				self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
				self.PINresultLabel.grid(sticky=W+E+N+S, pady=210)
				self.PINenteredtimeout.start()
				# self.smsDigitsLabel.grid_forget()
				
				# self.SMSresultLabel = ttk.Label(self.tk, text="Incorrect SMS\nCode Entered!")
				# self.SMSresultLabel.config(font='size, 20', justify='center', anchor='center')
				# self.SMSresultLabel.grid(sticky=tk.W+tk.E, pady=210)
				
				# self.SMSenteredtimeout = threading.Timer(10, self.returnToIdle_fromSMSentered)
				# self.SMSenteredtimeout.start()
				# self.PINresultLabel = ttk.Label(self.tk, text="Thank You, Now\nPlease Enter Code\nfrom SMS\n")
				# self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
				# self.PINresultLabel.grid(columnspan=3, sticky=tk.W+tk.E, pady=20)
				
				# self.smsDigitsLabel = ttk.Label(self.tk, text="Digits Entered: 0", font='size, 18', justify='center', anchor='center')
				# self.smsDigitsLabel.grid(columnspan=3, sticky=tk.W+tk.E)
				
				# smsCode = self.sendSMScode(mobileNumber)
				# smsCodeEntered = ''
				
				# keypad = [
				# 	'1', '2', '3',
				# 	'4', '5', '6',
				# 	'7', '8', '9',
				# 	'', '0', '',
				# ]
								
				# create and position all buttons with a for-loop
				# r, c used for row, column grid values
			# 	r = 4
			# 	c = 0
			# 	n = 0
			# 	# list(range()) needed for Python3
			# 	self.btn = list(range(len(keypad)))
			# 	for label in keypad:
			# 		# partial takes care of function and argument
			# 		#cmd = partial(click, label)
			# 		# create the button
			# 		self.btn[n] = tk.Button(self.tk, text=label, font='size, 18', width=4, height=1, command=lambda digitPressed=label:self.smsCodeEnteredInput(digitPressed, smsCode))
			# 		# position the button
			# 		self.btn[n].grid(row=r, column=c, ipadx=10, ipady=10)
			# 		# increment button index
			# 		n += 1
			# 		# update row/column position
			# 		c += 1
			# 		if c > 2:
			# 			c = 0
			# 			r += 1
				
			# 	self.SMSentrytimeout = threading.Timer(60, self.returnToIdle_fromSMSentry)
			# 	self.SMSentrytimeout.start()
				
			# else:
			# 	self.PINresultLabel = ttk.Label(self.tk, text="Incorrect PIN\nEntered!")
			# 	self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
			# 	self.PINresultLabel.grid(sticky=tk.W+tk.E, pady=210)
			# 	self.PINenteredtimeout.start()
				
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