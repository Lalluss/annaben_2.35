from pyrogram import Client, filters
from pyrogram.types import *
import requests 


@Client.on_message(filters.command("write"))
async def handwriting(client, message):
    if len(message.command) < 2:
        return await message.reply_text("» Give some text to write...")
    m = await message.reply_text("» I writing please wait...")
    name = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 1)[1].replace(" ", "%20")
    )
    API = "https://apis.xditya.me/write?text=" + name
    url = requests.get(API).url
    await m.edit("» Uploading...")
    me = await client.get_me()
    await message.reply_photo(url, caption=f"""**~ Request by {message.from_user.mention}**\n
**~ Made by @lallu_tgs**""",
    reply_markup=InlineKeyboardMarkup([[ InlineKeyboardButton(text="Download Link", url=url)]]))
