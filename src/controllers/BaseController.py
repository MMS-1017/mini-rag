# parent class having the common properties between all the controllers
from helpers.config import get_settings, Settings
import os
import random
import string

class BaseController:
    
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(self.base_dir, "assets/files")

        # self.files_dir = self.base_dir + "/assets/files" 
        # ==> 
        # is also correct, but using os.path.join is more robust across different OS
    
    def generate_random_string(self, length: int=12):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for _ in range(length))