import os
from urllib.parse import urlparse


Current_dir = os.path.dirname(os.path.abspath(__file__)) # Get the current directory of this script
ReconnResult_path = os.path.join(Current_dir, "ReconnResult")

def URLS_Handler():
    """
    Handles URLs by checking if they are valid and then processing them.
    """
    Alive_param_urls = os.path.join(ReconnResult_path, "param_urls.txt")

    open_alive_param_urls = open(Alive_param_urls, "r")
    URL_file_contents = open_alive_param_urls.readlines() #This returns a list of the lines in the file

    open_alive_param_urls.close()


URLS_Handler()