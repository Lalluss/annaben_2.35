from pyrogram import filters
from pyrogram.types import Message
from pyrogram.types.bots_and_keyboards.inline_keyboard_button import InlineKeyboardButton
from pyrogram.types.bots_and_keyboards.inline_keyboard_markup import InlineKeyboardMarkup
from pyrogram import Client 
from telegraph import upload_file

@Client.on_message(filters.command("txt"))
async def txt(client, message: Message):
    reply = message.reply_to_message

    if not reply or not reply.text:
        return await message.reply("Reply to a text message")

    if len(message.command) < 2:
        return await message.reply("**Usage:**\n /txt [Page name]")

    page_name = message.text.split(None, 1)[1]
    page = client.create_page(
        page_name, html_content=(reply.text.html).replace("\n", "<br>")
    )
    return await message.reply(
        f"**Posted:** {page['url']}",reply_markup=InlineKeyboardMarkup([ 
        [InlineKeyboardButton('View 💫' , url=f"{page['url']}")]
    ]),disable_web_page_preview=True,
    )
        

@Client.on_message(filters.command('tm'))
def tm(clinet,message):
    reply = message.reply_to_message
    if not reply:
          return message.reply_text("Reply to a **Media** to get a permanent telegra.ph link.")
    if reply.text:
          return message.reply_text("Reply to a **Media** to get a permanent telegra.ph link.")
    msg = message.reply_text("downloading")
    if reply.media:
        path = reply.download()
        fk = upload_file(path)
        for x in fk:
           url = "https://telegra.ph" + x
    msg.edit("uploading")
    buttons = [[InlineKeyboardButton('View 💫' , url=f"{url}")]] 
    if url.endswith("jpg"):
             message.reply_photo(url,caption=f"{url}",reply_markup=InlineKeyboardMarkup(buttons))
    elif url.endswith("mp4"):
             message.reply_animation(url,caption=f"{url}",reply_markup=InlineKeyboardMarkup(buttons))
    msg.delete()
