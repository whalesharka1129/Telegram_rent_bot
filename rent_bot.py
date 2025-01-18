import logging
from collections import defaultdict
from typing import DefaultDict, Optional, Set
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ExtBot,
)
import asyncio
import os
import json
import dotenv
import requests
from getRate import convert_usd_to_eth

dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")
ENDPOINT = os.getenv("ENDPOINT")
# Global Variables
space = " ;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;&#xA0;"

def load_json_data(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


data = load_json_data("data.json")

descText = f"""
🚀 <b>Welcome to Nimbus GPU Rent Bot !</b>\n
With Nimbus GPU Rental Bot, you can easily buy or sell high-performance servers directly from your Telegram. No more complex setups or mandatory KYC—just straightforward, secure access at your fingertips. Start now and experience the future of cloud computing!

Supported Blockchains:

✅ ETH

Supported Service:
👜CPU - Shared CPU
👜GPU - A40, A100

Supported GPU Configurations:

Nvidia: A100, A40 AI-Enabled GPUs

The user is free to pick the configuration of their choice and the bot will take care of the rest.
"""
helpContent = f"""
<b>🔍 Nimbus GPU Rent Bot help 🔍</b>\n
Some content comes here...
\n\n\n\n\n
"""
certification = f"\n\n<b>Made with ❤️ by The Nimbus Team</b>{space}"
homepageBtn = InlineKeyboardButton(
    text="🌎Website", url="https://dapp.nimbusnetwork.io/"
)
myServerBtn = InlineKeyboardButton(text="💻   My Servers", callback_data="myServerBtn")
buyCPUBtn = InlineKeyboardButton(text="👜   Rent CPU", callback_data="buyCPUBtn")
buyGPUBtn = InlineKeyboardButton(text="👜   Rent GPU", callback_data="buyGPUBtn")
profileBtn = InlineKeyboardButton(text="💻  Profile", callback_data="profileBtn")
analyticsBtn = InlineKeyboardButton(
    text="📊    Analytics", callback_data="analyticsBtn"
)
docsBtn = InlineKeyboardButton(text="📜   Help", callback_data="helpBtn")
mainKeyboardMarkup = InlineKeyboardMarkup(
    [
        [myServerBtn],
        [buyCPUBtn, buyGPUBtn],
        # [profileBtn],
        # [analyticsBtn],
        [homepageBtn, docsBtn],  # This is a row with two buttons
    ]
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class ChatData:
    """Custom class for chat_data. Here we store data per message."""

    def __init__(self) -> None:
        self.data = {
            "state": "default",
            "ChatID":"",
            "nodes":[],
            "walletAddr":"",
            "serviceType": "N/A",
            "processType": "N/A",
            "processDetail": "N/A",
            "processDetailIndex": 0,
            "region": "N/A",
            "osType": "N/A",
            "osDetail": "N/A",
            "monthlyCost": "N/A",
            "monthlyCost_usd": 0,
            "monthlyCost_eth": 0,
            "tagLine": "",
        }
        self.clicks_per_message: DefaultDict[int, int] = defaultdict(int)

    def __setitem__(self, key, value):
        """Allow setting arbitrary attributes."""
        self.data[key] = value

    def __getitem__(self, key):
        """Allow getting arbitrary attributes."""
        return self.data.get(key)

class CustomContext(CallbackContext[ExtBot, dict, ChatData, dict]):
    """Custom class for context."""

    def __init__(
        self,
        application: Application,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ):
        super().__init__(application=application, chat_id=chat_id, user_id=user_id)
        self._message_id: Optional[int] = None

    @property
    def bot_user_ids(self) -> Set[int]:
        """Custom shortcut to access a value stored in the bot_data dict"""
        return self.bot_data.setdefault("user_ids", set())

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

    @classmethod
    def from_update(cls, update: object, application: "Application") -> "CustomContext":
        """Override from_update to set _message_id."""
        # Make sure to call super()
        context = super().from_update(update, application)

        if (
            context.chat_data
            and isinstance(update, Update)
            and update.effective_message
        ):
            # pylint: disable=protected-access
            context._message_id = update.effective_message.message_id

        # Remember to return the object
        return context

def initializeOrderDetail(context):
    context.chat_data["state"] = "default"
    context.chat_data["ChatId"] = ""
    context.chat_data["walletAddr"] = ""
    context.chat_data["serviceType"] = "N/A"
    context.chat_data["processType"] = "N/A"
    context.chat_data["processDetail"] = "N/A"
    context.chat_data["processDetailIndex"] = 0
    context.chat_data["region"] = "N/A"
    context.chat_data["osType"] = "N/A"
    context.chat_data["osDetail"] = "N/A"
    context.chat_data["monthlyCost"] = "N/A"
    context.chat_data["monthlyCost_usd"] = 0
    context.chat_data["tagLine"] = ""

async def orderSubmit(context: CustomContext)-> None:
    data = {
        "serviceType":context.chat_data["serviceType"],
        "processType":context.chat_data["processType"],
        "processDetail":context.chat_data["processDetail"],
        "region":context.chat_data["region"],
        "osType":context.chat_data["osType"],
        "osDetail":context.chat_data["osDetail"],
        "monthlyCost":context.chat_data["monthlyCost_eth"]
    }
    response = requests.post(f"{ENDPOINT}/api/tgorder/{context.chat_data["ChatID"]}", json=data)
    if response.status_code == 200:
        res = response.json()
        context.chat_data["walletAddr"] = res['addr']
        print("Response content:", context.chat_data["walletAddr"])
    else:
        print("POST request failed with status code:", response.status_code)

async def getNodes(context: CustomContext)-> None:
    response = requests.get(f"{ENDPOINT}/api/tgorder/getorder/{context.chat_data["ChatID"]}")
    if response.status_code == 200:
        res = response.json()
        context.chat_data["nodes"] = res['nodes']
        print("Response content:", context.chat_data["nodes"])
    else:
        print("POST request failed with status code:", response.status_code)

async def clickHandler(update: Update, context: CustomContext) -> None:
    """Handle the button click."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button click

    # Extract the callback data from the clicked button
    callback_data = query.data
    replyKeyBoardMarkUp = InlineKeyboardMarkup([])
    responseText = ""
    if callback_data == "buyCPUBtn":
        context.chat_data["state"] = "buyCPUBtn"
        replyKeyBoardMarkUp = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"💻   {option}", callback_data=f"processType_{i}"
                    )
                ]
                for i, option in enumerate(data["CPU"]["assets"])
            ]
        )
        context.chat_data["serviceType"] = "CPU"
        context.chat_data["tagLine"] = f"Step 1 - Select a CPU Type"
        responseText = f"""
<b>Your Current Configuration:</b>\n
➡️  <b>Service:</b>    {context.chat_data["serviceType"]} Rent
➡️  <b>Processor Type:</b>     {context.chat_data["processType"]}
➡️  <b>Processor Detail:</b>     {context.chat_data["processDetail"]}
➡️  <b>Region:</b>     {context.chat_data["region"]}
➡️  <b>Os:</b>     {context.chat_data["osType"]}
➡️  <b>Os Version:</b>     {context.chat_data["osDetail"]}
➡️  <b>Monthly Cost:</b>     {context.chat_data["monthlyCost"]}
-------- ⬇️ --------
{context.chat_data["tagLine"]}
"""
    elif callback_data == "buyGPUBtn":
        context.chat_data["state"] = "buyGPUBtn"
        replyKeyBoardMarkUp = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"💻   {option}", callback_data=f"processType_{i}"
                    )
                ]
                for i, option in enumerate(data["GPU"]["assets"])
            ]
        )
        context.chat_data["serviceType"] = "GPU"
        context.chat_data["tagLine"] = f"Step 1 - Select a GPU Type"
        responseText = f"""
<b>Your Current Configuration:</b>\n 
➡️  <b>Service:</b>    {context.chat_data["serviceType"]} Rent
➡️  <b>Processor Type:</b>     {context.chat_data["processType"]}
➡️  <b>Processor Detail:</b>     {context.chat_data["processDetail"]}
➡️  <b>Region:</b>     {context.chat_data["region"]}
➡️  <b>Os:</b>     {context.chat_data["osType"]}
➡️  <b>Os Version:</b>     {context.chat_data["osDetail"]}
➡️  <b>Monthly Cost:</b>     {context.chat_data["monthlyCost"]}
-------- ⬇️ --------
{context.chat_data["tagLine"]}
"""
    elif callback_data.startswith("processType_"):
        selectedIndex = int(callback_data.split("_")[1])
        process_type = data[context.chat_data["serviceType"]]["assets"][selectedIndex]
        replyKeyBoardMarkUp = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"💻   {option}", callback_data=f"processDetail_{i}"
                    )
                ]
                for i, option in enumerate(
                    data[context.chat_data["serviceType"]]["assetsDetail"][process_type]
                )
            ]
        )
        context.chat_data["processType"] = process_type
        context.chat_data["tagLine"] = (
            f"Step 2 - Select a Process Detail"
        )
        responseText = f"""
<b>Your Current Configuration:</b>\n 
➡️  <b>Service:</b>    {context.chat_data["serviceType"]} Rent
➡️  <b>Processor Type:</b>     {context.chat_data["processType"]}
➡️  <b>Processor Detail:</b>     {context.chat_data["processDetail"]}
➡️  <b>Region:</b>     {context.chat_data["region"]}
➡️  <b>Os:</b>     {context.chat_data["osType"]}
➡️  <b>Os Version:</b>     {context.chat_data["osDetail"]}
➡️  <b>Monthly Cost:</b>     {context.chat_data["monthlyCost"]}
-------- ⬇️ --------
{context.chat_data["tagLine"]}
"""
    elif callback_data.startswith("processDetail_"):
        selectedIndex = int(callback_data.split("_")[1])
        context.chat_data["processDetailIndex"] = selectedIndex
        process_detail = data[context.chat_data["serviceType"]]["assetsDetail"][
            context.chat_data["processType"]
        ][selectedIndex]
        monthly_cost = data[context.chat_data["serviceType"]]["assetsCosts"][
            context.chat_data["processType"]
        ][selectedIndex]
        context.chat_data["monthlyCost_usd"] = monthly_cost
        replyKeyBoardMarkUp = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"🌎   {option}", callback_data=f"processLocations_{i}"
                    )
                ]
                for i, option in enumerate(
                    data[context.chat_data["serviceType"]]["assetsLocations"][
                        context.chat_data["processType"]
                    ][selectedIndex]
                )
            ]
        )
        context.chat_data["processDetail"] = process_detail
        context.chat_data["tagLine"] = (
            f"Step 3 - Select a Process Location"
        )
        responseText = f"""
<b>Your Current Configuration:</b>\n 
➡️  <b>Service:</b>    {context.chat_data["serviceType"]} Rent
➡️  <b>Processor Type:</b>     {context.chat_data["processType"]}
➡️  <b>Processor Detail:</b>     {context.chat_data["processDetail"]}
➡️  <b>Region:</b>     {context.chat_data["region"]}
➡️  <b>Os:</b>     {context.chat_data["osType"]}
➡️  <b>Os Version:</b>     {context.chat_data["osDetail"]}
➡️  <b>Monthly Cost:</b>     {context.chat_data["monthlyCost"]}
-------- ⬇️ --------
{context.chat_data["tagLine"]}
"""
    elif callback_data.startswith("processLocations_"):
        selectedIndex = int(callback_data.split("_")[1])
        region_temp = data[context.chat_data["serviceType"]]["assetsLocations"][
            context.chat_data["processType"]
        ][context.chat_data["processDetailIndex"]][selectedIndex]
        replyKeyBoardMarkUp = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"📀   {option}", callback_data=f"processOs_{i}"
                    )
                ]
                for i, option in enumerate(data[context.chat_data["serviceType"]]["os"])
            ]
        )
        context.chat_data["region"] = region_temp
        context.chat_data["tagLine"] = f"Step 4 - Select a Os Type"
        responseText = f"""
<b>Your Current Configuration:</b>\n 
➡️  <b>Service:</b>    {context.chat_data["serviceType"]} Rent
➡️  <b>Processor Type:</b>     {context.chat_data["processType"]}
➡️  <b>Processor Detail:</b>     {context.chat_data["processDetail"]}
➡️  <b>Region:</b>     {context.chat_data["region"]}
➡️  <b>Os:</b>     {context.chat_data["osType"]}
➡️  <b>Os Version:</b>     {context.chat_data["osDetail"]}
➡️  <b>Monthly Cost:</b>     {context.chat_data["monthlyCost"]}
-------- ⬇️ --------
{context.chat_data["tagLine"]}
"""
    elif callback_data.startswith("processOs_"):
        selectedIndex = int(callback_data.split("_")[1])
        os_Type = data[context.chat_data["serviceType"]]["os"][selectedIndex]
        os_Type_clean = os_Type.lower().replace(" ", "")
        replyKeyBoardMarkUp = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"📀   {option}", callback_data=f"processOsDetail_{i}"
                    )
                ]
                for i, option in enumerate(data["Os"][os_Type_clean])
            ]
        )
        context.chat_data["osType"] = os_Type
        context.chat_data["tagLine"] = f"Step 5 - Select a Os Detail"
        responseText = f"""
<b>Your Current Configuration:</b>\n 
➡️  <b>Service:</b>    {context.chat_data["serviceType"]} Rent
➡️  <b>Processor Type:</b>     {context.chat_data["processType"]}
➡️  <b>Processor Detail:</b>     {context.chat_data["processDetail"]}
➡️  <b>Region:</b>     {context.chat_data["region"]}
➡️  <b>Os:</b>     {context.chat_data["osType"]}
➡️  <b>Os Version:</b>     {context.chat_data["osDetail"]}
➡️  <b>Monthly Cost:</b>     {context.chat_data["monthlyCost"]}
-------- ⬇️ --------
{context.chat_data["tagLine"]}
"""
    elif callback_data.startswith("processOsDetail_"):
        selectedIndex = int(callback_data.split("_")[1])
        os_Detail = data["Os"][context.chat_data["osType"].lower().replace(" ", "")][
            selectedIndex
        ]
        replyKeyBoardMarkUp = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=f"Confirm", callback_data=f"confirm"),
                    InlineKeyboardButton(text=f"Cancel", callback_data=f"cancel"),
                ]
            ]
        )

        context.chat_data["osDetail"] = os_Detail
        context.chat_data["tagLine"] = (
            f"Please confirm your configuration"
        )
        context.chat_data["monthlyCost"]=f"$ {context.chat_data["monthlyCost_usd"]}"
        responseText = f"""
<b>Your Current Configuration:</b>\n 
➡️  <b>Service:</b>    {context.chat_data["serviceType"]} Rent
➡️  <b>Processor Type:</b>     {context.chat_data["processType"]}
➡️  <b>Processor Detail:</b>     {context.chat_data["processDetail"]}
➡️  <b>Region:</b>     {context.chat_data["region"]}
➡️  <b>Os:</b>     {context.chat_data["osType"]}
➡️  <b>Os Version:</b>     {context.chat_data["osDetail"]}
➡️  <b>Monthly Cost:</b>     {context.chat_data["monthlyCost"]}
-------- ⬇️ --------
{context.chat_data["tagLine"]}
"""
    elif callback_data == "confirm":
        context.chat_data["state"] = "orderCompleted"
        context.chat_data["monthlyCost_eth"] = convert_usd_to_eth(context.chat_data["monthlyCost_usd"])
        await orderSubmit(context)
        responseText = f"""
👋Dear valued customer\n
Due to our beta version, it may take 10 to 30 minutes for your order to be approved.\n
Your server order has been placed. Please deposit <code> {context.chat_data["monthlyCost_eth"]} ETH </code> to the allocated wallet address below:\n
<b>Deposit address:</b> <code> {context.chat_data["walletAddr"]} </code>\n
Once the payment is detected, your server will be provisioned, and you will receive a DM with the login details.

<b>Note: If you don't make a deposit within 15 minutes, your order will be ignored.</b>

Thank you for your order!
"""
    elif callback_data == "cancel":
        responseText = f"{descText}{certification}"
        replyKeyBoardMarkUp = mainKeyboardMarkup
    elif callback_data == "myServerBtn":
        await getNodes(context)
        context.chat_data["state"] = "myServerBtn"
        servers = context.chat_data["nodes"]
        print("servers======>", servers)
        if servers:
            for node in context.chat_data["nodes"]:
                responseText += f"""
<b>ServerDetail:</b>{node["processDetail"]}
💻<b>IP Address:</b>{node["main_ip"]}
🔑<b>Password:</b>  {node["password"]}\n
                """
        else:
            responseText = f"No Servers"

    elif callback_data == "analyticsBtn":
        context.chat_data["state"] = "analyticsBtn"

    elif callback_data == "helpBtn":
        context.chat_data["state"] = "helpBtn"
        replyKeyBoardMarkUp = mainKeyboardMarkup
        responseText = f"{descText}{certification}"

    await query.message.reply_html(responseText, reply_markup=replyKeyBoardMarkUp)

async def myservers(updata:Update, context: CustomContext):
    await getNodes(context)
    responseText = ""
    servers = context.chat_data["nodes"]
    if servers:
        for node in context.chat_data["nodes"]:
            responseText += f"""
<b>ServerDetail:</b>{node["processDetail"]}
💻<b>IP Address:</b>{node["main_ip"]}
🔑<b>Password:</b>  {node["password"]}\n
                """
    else:
        responseText="No Servers"
    await updata.message.reply_html(responseText)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userName = update.message.chat.username
    userId = str(update.message.chat.id)
    storage_file_path = "userList.json"
    thread_ids = {}
    if os.path.exists(storage_file_path):
        with open(storage_file_path, "r") as file:
            thread_ids = json.load(file)
    else:
        with open(storage_file_path, "w") as file:
            json.dump(thread_ids, file)
    all_keys = list(thread_ids.keys())
    # Check if the specific user_id exists in the dictionary
    if userId in all_keys:
        pass
    else:
        thread_ids[userId] = userName
        # Save the updated dictionary to the storage file
        with open(storage_file_path, "w") as file:
            json.dump(thread_ids, file)
    initializeOrderDetail(context)
    context.chat_data["ChatID"] = userId
    inputData = update.message.text.removeprefix("/start").strip()
    response_text = f"{descText}{certification}"

    await update.message.reply_html(response_text, reply_markup=mainKeyboardMarkup)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response_text = f"{helpContent}{certification}"
    await update.message.reply_html(response_text, reply_markup=mainKeyboardMarkup)

def main() -> None:
    """Run the bot."""
    context_types = ContextTypes(context=CustomContext, chat_data=ChatData)
    application = (
        Application.builder().token(TOKEN).context_types(context_types).build()
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rent", start))
    application.add_handler(CommandHandler("myservers", myservers))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CallbackQueryHandler(clickHandler))
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
