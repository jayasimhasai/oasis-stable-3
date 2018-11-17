from logger import logger_variable
import os

n = 'fg'
files = ' ssd'
logger_variable(n,files)
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
print(THIS_FOLDER)