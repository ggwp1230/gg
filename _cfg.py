# -*- coding: utf8 -*-
import configparser as cparse
import os


config_path = 'data/config.ini'

def check_file():
	if not os.path.exists(config_path):
		create_config()
		
		print('The configuration file has been created. Fill in the configuration values.')
		exit()

def create_config():
	config = cparse.ConfigParser()
	config.add_section("SETTING")
	config.set("SETTING", "BOT_TOKEN", "token")
	config.set("SETTING", "ADMIN_ID", "0")
	config.set("SETTING", "DEBUG", "False")
	with open(config_path, "w") as config_file:
		config.write(config_file)

def get(value):
	config = cparse.ConfigParser()
	config.read(config_path, encoding='utf-8')

	a = config.get("SETTING", value)
	return a

def set(value, data):
	config = cparse.ConfigParser()
	config.read(config_path, encoding='utf-8')
	
	a = config.set("SETTING", value, data)
	with open(config_path, "w") as config_file:
		config.write(config_file)

## __init__ ##
check_file()