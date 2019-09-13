# import re
# def required(value, message):
#     if not value:
#         raise ValueError(message)
#     return value

# def matches(value, regex, message):
#     if value and not regex.match(value):
#         raise ValueError(message)
#     return value

class UserObject():

    def __init__(self, user_id, name, image_id, pin, rfid_code, image_url):
        self.user_id = user_id
        self.name = name
        self.image_id = image_id
        self.pin = pin
        self.rfid_code = rfid_code
        self.image_url = image_url

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def image_id(self):
        return self._image_id

    @image_id.setter
    def image_id(self, value):
        self._image_id = value
    
    @property
    def pin(self):
        return self._pin

    @pin.setter
    def pin(self, value):
        self._pin = value

    @property
    def rfid_code(self):
        return self._rfid_code

    @rfid_code.setter
    def rfid_code(self, value):
        self._rfid_code = value

    @property
    def image_url(self):
        return self._image_url

    @image_url.setter
    def image_url(self, value):
        self._image_url = value

class LogObject():
    
    def __init__(
            self, 
            access_id, 
            rfid_presented, 
            rfid_preseneted_datetime, 
            rfid_granted, 
            pin_entered, 
            pin_entered_datetime, 
            pin_granted, 
            image
        ):
        self.access_id = access_id
        self.rfid_presented = rfid_presented
        self.rfid_preseneted_datetime = rfid_preseneted_datetime
        self.rfid_granted = rfid_granted
        self.pin_entered = pin_entered
        self.pin_entered_datetime = pin_entered_datetime
        self.pin_granted = pin_granted
        self.image = image

    @property
    def access_id(self):
        return self._access_id

    @access_id.setter
    def access_id(self, value):
        self._access_id = value

    @property
    def rfid_presented(self):
        return self._rfid_presented

    @rfid_presented.setter
    def rfid_presented(self, value):
        self._rfid_presented = value

    @property
    def rfid_presentedrfid_presented_datetime(self):
        return self._rfid_presentedrfid_presented_datetime

    @rfid_presentedrfid_presented_datetime.setter
    def rfid_presentedrfid_presented_datetime(self, value):
        self._rfid_presentedrfid_presented_datetime = value
    
    @property
    def rfid_granted(self):
        return self._rfid_granted

    @rfid_granted.setter
    def rfid_granted(self, value):
        self._rfid_granted = value

    @property
    def pin_entered(self):
        return self._pin_entered

    @pin_entered.setter
    def pin_entered(self, value):
        self._pin_entered = value

    @property
    def pin_entered_datetime(self):
        return self._pin_entered_datetime

    @pin_entered_datetime.setter
    def pin_entered_datetime(self, value):
        self._pin_entered_datetime = value
    
    @property
    def pin_granted(self):
        return self._pin_granted

    @pin_granted.setter
    def pin_granted(self, value):
        self._pin_granted = value

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value