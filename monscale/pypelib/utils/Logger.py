import logging
from django.conf import settings
'''
        @author: msune
        @organization: i2CAT, OFELIA FP7

       	Simple Logger wrapper 
'''

logging.basicConfig(format='%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=settings.LOG_LEVEL)


class Logger():
	@staticmethod
	def getLogger():
		#Simple wrapper. Ensures logging is always correctly configured (logging.basicConfig is executed)
		return logging.getLogger()
