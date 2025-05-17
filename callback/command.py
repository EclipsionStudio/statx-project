from handlers.start import start_handler
from handlers.help import help_handler
from handlers.login import login_handler
from handlers.info import info_handler

def command_handler(call):
    data = call.data[8:]

    if data.startswith("start"):
        start_handler(call.message)
    
    elif data.startswith("help"):
        help_handler(call.message)
    
    elif data.startswith("login"):
        login_handler(call.message)
    
    elif data.startswith("info"):
        info_handler(call.message)