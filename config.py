import os

class Config:
	SECRET_KEY = 'clave_secreta'

class Development(Config):
	DEBUG = True
	SECRET_KEY = 'clave_secreta'
	
class Testing(Config):
	TESTING = True

class Production(Config):
	pass	

config = {
	'development': Development,
	'testing': Testing,
	'production': Production,
	'default': Development
}