import logging
from collections import defaultdict
from typing import DefaultDict, Optional, Set
from telegram import (
     InlineKeyboardButton,
     InlineKeyboardMarkup,
     Update
)
from telegram.ext import (
     Application,
     CommandHandler,
     MessageHandler,
     CallbackQueryHandler,
     filters,
     ContextTypes,
     ExtBot,
)

import asyncio
import dotenv
import os

dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")

def main()-> None:
     "Run the Bot"
     
     context_types = ContextTypes(context=CustomContext, chat_data=ChatData)
     application = Application.builder().token(TOKEN).context_types().build()
     application.add_handler(CommandHandler("start", start))
     application.add_handler(CommandHandler("rent", start))
     application.add_handler(CommandHandler("myservers", myservers))
     application.add_handler(CommandHandler("help", help))
     application.add_handler(CallbackQueryHandler(clickHandler))
     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy)
     application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":  
    main()