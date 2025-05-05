import handlers
import callback 
import modules
import translations

print(">> LOAD FUNC", handlers.data, callback.data, translations.data, modules.data, "LOAD ENDED <<\n",sep=" <<\n>> ")
print(modules.bot_info())

modules.bot.polling()