from modules.global_init import bot
from handlers.start import start_handler
from handlers.help import help_handler
from handlers.login import login_handler
from handlers.compare import compare_handler
from handlers.info import info_handler
# from handlers.auto_msg import llm_analyse_handler


data = "handlers loaded"


@bot.message_handler(commands=["start"])
def start_init(message):
    start_handler(message)


@bot.message_handler(commands=["help"])
def help_init(message):
    help_handler(message)


@bot.message_handler(commands=["info"])
def info_init(message):
    info_handler(message)


@bot.message_handler(commands=["login"])
def login_init(message):
    login_handler(message)


@bot.message_handler(commands=["compare"])
def compare_init(message):
    compare_handler(message)