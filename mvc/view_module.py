import threading
import time
from tkinter import *
from tkinter import ttk
from threading import Thread
from evdev import InputDevice
from select import select

class DoorLockView(Tk):
	def __init__(self):
		super().__init__()
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=1)
		self.columnconfigure(2, weight=1)
		self.columnconfigure(3, weight=1)
		self.remaining = 0
		self.meraki_url = ''
		self.meraki_thread = None
		self.pin = ''
		self.access_log_id = ''
		
		self.attributes('-zoomed', True)
		self.attributes('-fullscreen', True)
		self.title('Three Factor Authentication Door Lock')
		self.config(cursor="none")
		self.PINentrytimeout = None
		
		self.show_idle()
		
		t = Thread(target=self.listen_rfid)
		t.daemon = True
		t.start()

	def set_ctrl(self, controller):
		self.controller = controller
		self.controller.initialize_gpio_board()
  
	def show_idle(self):
		self.welcomeLabel = ttk.Label(self, text="Please Present\nYour Token")
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
		self.update
	
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
		self.controller.door_contorl('LOW')
		self.face_match_forget()
		self.show_idle()
		
	def returnToIdle_fromFaceMatchFail(self):
		self.face_match_forget()
		self.show_idle()
	
	def countdown(self):
		'''start countdown 10 seconds before new year starts'''
		for k in range(5, 0, -1):
			self.countdownTimerLabel["text"] = k
			self.update()
			time.sleep(1)
		self.countdownTimerLabel["text"] = "Picture Taken"
		self.update()
		return self.controller.retrieve_snapshot()

	def listen_rfid(self):
		
		keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
		dev = InputDevice('/dev/input/event0')
		rfid_presented = ""

		while True:
			r,w,x = select([dev], [], [])
			for event in dev.read():
				if event.type==1 and event.value==1:
						if event.code==28:

							rfid_user = self.controller.get_user_info(rfid_presented)
						
							if len(rfid_user) != 1:
								self.welcomeLabel.config(text="ACCESS DENIED", justify='center', anchor='center')
								
								# Log access attempt
								localtime = time.asctime( time.localtime(time.time()) )
								payload = {
									'rfid_presented' : f'{rfid_presented}',
									'rfid_presented_datetime' : f'{localtime}',
									'rfid_granted' : 0
								}
								self.controller.post_to_log('alog', payload)
								self.welcomeLabel.grid_forget()
								self.show_idle()
							else:
								user_info = rfid_user[0]
								userPin = str(user_info['pin'])
								image_url = user_info['image']
								self.welcomeLabel.grid_forget()
								self.validUser = ttk.Label(self, text=f"Welcome\n {user_info['name']}!", font='size, 15', justify='center', anchor='center')
								self.validUser.grid(columnspan=3, sticky=W+E)
								self.image = PhotoImage(file='image75.gif')
								self.photoLabel = ttk.Label(self, image=self.image, justify='center', anchor='center')
								self.photoLabel.grid(columnspan=3, sticky=W+E)
								
								self.enterPINlabel = ttk.Label(self, text='Please enter your PIN:', font='size, 18', justify='center', anchor='center')
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
								for label in keypad:
									# create the button
									self.btn[n] = Button(self, text=label, font='size, 16', width=4, height=1, command=lambda digitPressed=label:self.codeInput(digitPressed, userPin, image_url))
									# position the button
									self.btn[n].grid(row=r, column=c, padx=15, ipady=0)
									# increment button index
									n += 1
									# update row/column position
									c += 1
									if c > 2:
										c = 0
										r += 1
								
								# Log access attempt
								localtime = time.asctime( time.localtime(time.time()) )
								payload = {
									'rfid_presented' : f'{rfid_presented}',
									'rfid_presented_datetime' : f'{localtime}',
									'rfid_granted' : 1
								}
								try:
									rfid_log = self.controller.post_to_log('alog', payload)
									self.access_log_id = rfid_log['_id']
								except Exception as e:
									print(e)
							
								self.PINentrytimeout = threading.Timer(10, self.returnToIdle_fromPINentry)
								self.PINentrytimeout.start()
								
								
								self.PINenteredtimeout = threading.Timer(5, self.returnToIdle_fromPINentry)
							
							rfid_presented = ""
						else:
							rfid_presented += keys[ event.code ]
							print(rfid_presented)

	def codeInput(self, value, userPin, user_image_id):
		self.pin += value
		pinLength = len(self.pin)
		
		self.enterPINlabel.config(text=f'Digits Entered: {pinLength}')
		
		if pinLength == 4:
			if self.PINentrytimeout:
				self.PINentrytimeout.cancel()
			self.pin_entry_forget()
			
			if self.pin == userPin:
				pin_granted = 1
			else:
				pin_granted = 0
			
			localtime = time.asctime( time.localtime(time.time()) )
			payload = {
				'pin_entered' : f'{self.pin}',
				'pin_entered_datetime' : f'{localtime}',
				'pin_granted' : f'{pin_granted}'
			}
			try:
				doc = self.controller.update_access_log_doc('alog', self.access_log_id, payload)
			except Exception as e:
				print(e)

			if self.pin == userPin:

				self.PINresultLabel = ttk.Label(self, text="Thank You, Please Look\nAt The Camera")
				self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
				self.PINresultLabel.grid(columnspan=3, sticky=W+E+N+S, pady=50)

				

				self.countdownTimerLabel = ttk.Label(self, text='5', width=10)
				self.countdownTimerLabel.config(font='size, 36', justify='center', anchor='center')
				self.countdownTimerLabel.grid(columnspan=3, sticky=W+E)

				self.meraki_url = self.countdown()

				self.pin_result_forget()

				self.face_match_label = ttk.Label(self, text='')
				self.face_match_label.config(font='size, 30', justify='center', anchor='center')
				self.face_match_label.grid(columnspan=3, sticky=W+E, pady=125)
				
				if self.meraki_url:
					user_db_photo =  self.controller.user_db_image_url('m', user_image_id)
					self.face_match_label['text'] = 'Comparing photo...'
					self.update()
					face_match = self.controller.compare_photos(user_db_photo, self.meraki_url)
					if face_match:
						self.face_match_label['text'] = 'Match!'
						self.update()
						self.controller.door_contorl('HIGH')
						self.doorOpenTimeout = threading.Timer(10, self.returnToIdle_fromAccessGranted)
						self.doorOpenTimeout.start()
					else:
						self.face_match_label['text'] = 'No Match'
						self.update()
						self.face_match_fail = threading.Timer(10, self.returnToIdle_fromFaceMatchFail)
						self.face_match_fail.start()
				else:
					self.face_match_label['text'] = 'Error...'
					self.update()
					self.snapshot_fail = threading.Timer(5, self.retruntoIdle_from_snapshot_fail)
					self.snapshot_fail.start()
			else:
				self.PINresultLabel = ttk.Label(self, text="Incorrect PIN\nEntered!")
				self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
				self.PINresultLabel.grid(columnspan=3, sticky=W+E+N+S, pady=125)
				self.PINenteredtimeout.start()
			self.pin = ''

