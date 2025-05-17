import handlers
import callback 
import modules
from modules.global_init import logger
import translations

logger.info(handlers.data)
logger.info(modules.data)
logger.info(callback.data)
logger.info(translations.data)

modules.bot_info()
modules.bot.polling()