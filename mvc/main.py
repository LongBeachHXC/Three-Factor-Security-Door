from view_module import DoorLockView
from door_lock_db import DoorLockDB
from controller import DoorLockController

def main():
	view = DoorLockView()
	db = DoorLockDB()
	ctrl = DoorLockController(db, view)
	view.set_ctrl(ctrl)
	ctrl.start()

if __name__ == "__main__":
	main()