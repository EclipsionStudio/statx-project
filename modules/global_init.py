from telebot import TeleBot
from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging
from logging.handlers import RotatingFileHandler
import os


bot = TeleBot(str(config('BOT_TOKEN')))

Base = declarative_base()
engine = create_engine('sqlite:///data/database.db3', echo=False)
Session = sessionmaker(bind=engine)


def get_session():
    return Session()



class CustomFormatter(logging.Formatter): 
	def format(self, record): 
		lvl = record.levelname 
		if lvl == "INFO":    
			record.levelname = "[I---]"
		elif lvl == "WARNING": 
			record.levelname = "[-W--]"
		elif lvl == "DEBUG": 
			record.levelname = "[--D-]"
		elif lvl == "ERROR": 
			record.levelname = "[---E]"
		return super().format(record)


def setup_logger() -> logging.Logger:
	logger = logging.getLogger("telebot")
	logger.setLevel(logging.DEBUG) 

	formatter = CustomFormatter('%(levelname)s [%(filename)s:%(lineno)-3d] %(message)s')

	log_path = os.path.join("logs", "app.log")
	os.makedirs(os.path.dirname(log_path), exist_ok=True)

	fh = RotatingFileHandler(log_path, maxBytes=10_000_000, backupCount=5, encoding="utf-8")
	fh.setLevel(logging.DEBUG)
	fh.setFormatter(formatter)

	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	ch.setFormatter(formatter)

	logger.addHandler(fh)
	logger.addHandler(ch)

	return logger

logger = setup_logger()