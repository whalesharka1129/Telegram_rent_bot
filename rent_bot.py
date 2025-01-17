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
     CallbackContext,
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

class ChatData:
     """Custom class fir the char_Data"""
     def __init__(self):
          self.data = {
               "state": "default",
               "ChatID":"",
               "nodes":[],
               "walletAddr":"",
               "serviceType":"N/A",
               "processDetail":"N/A",
               "processDetailIndex":0,
               "region":"N/A",
               "osType":"N/A",
               "osDetail":"N/A",
               "monthlyCost":"N/A",
               "monthlyCost_usd":"N/A",
               "monthlyCost_eth":"N/A",
               "tagLine":"",
          }
          self.clicks_per_message: DefaultDict[int, int] = defaultdict(int)

     def __setItem__(self, key, value):
          """Allow setting arbitary attributes"""
          self.data[key] = value

     def __getItem__(self, key):
          """Allow getting arbitary attribtes"""
          return self.data.get[key]
class CustomContext(CallbackContext[ExtBot, dict, ChatData, dict]):     
     """Custom class for context"""
     def __init__(
          self,
          application: Application,
          chat_id: Optional[int] = None,
          user_id: Optional[int] = None,
          ):
            super().__init__(application=application, chat_id = chat_id, user_id= user_id)
            self._message_id: Optional[int] = None
     @property
     def bot_user_ids(self) -> Set[int]:
          """Custom shortcut to access a value"""
          return self.bot_data.setdefault("users_ids", set())
     @property
     def message_clicks(self) -> Optional[int]:
        """Access the number of clicks for the message this context object was built for."""
        if self._message_id:
            return self.chat_data.clicks_per_message[self._message_id]
        return None

     @message_clicks.setter
     def message_clicks(self, value: int) -> None:
        """Allow to change the count"""
        if not self._message_id:
            raise RuntimeError(
                "There is no message associated with this context object."
            )
        self.chat_data.clicks_per_message[self._message_id] = value
     



def main()-> None:
     "Run the Bot"
     
     context_types = ContextTypes(context=CustomContext, chat_data=ChatData)
     application = Application.builder().token(TOKEN).context_types(context_types).build()
     application.add_handler(CommandHandler("start", start))
     application.add_handler(CommandHandler("rent", start))
     application.add_handler(CommandHandler("myservers", myservers))
     application.add_handler(CommandHandler("help", help))
     application.add_handler(CallbackQueryHandler(clickHandler))
     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy)
     application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":  
    main()