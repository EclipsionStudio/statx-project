from modules import bot
from callback.command import command_handler
# from callback.func import func_handler

data = "Callback handlers loaded"


@bot.callback_query_handler(func=lambda call: call.data.startswith("command:"))
def command_init(callback):
    command_handler(callback)


# @bot.callback_query_handler(func=lambda call: call.data.startswith("func:"))
# def func_init(callback):
#     func_handler(callback)
