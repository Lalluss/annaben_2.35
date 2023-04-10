from pyrogram import Client, filters
from pyrogram.types import *




@Client.on_message(filters.command("whisper"))
async def whisper(client, message):
      global name, text, user
      name = message.from_user.first_name
      mention = message.from_user.mention
      if len(message.command) <2:
          return await message.reply("ɢɪᴠᴇ  ᴀ  ᴜsᴇʀɪᴅ  ᴡʜᴏ  ᴡᴀɴᴛ  sᴇᴇ  ʏᴏᴜʀ  ʜɪᴅᴅᴇɴ  ᴍᴇssᴀɢᴇ")
      elif len(message.command) <3:
          return await message.reply("ɢɪᴠᴇ  ᴍᴇssᴀɢᴇ  ᴛᴏ  ᴄʀᴇᴀᴛᴇ  ᴡʜɪsᴘᴇʀ ᴍᴇssᴀɢᴇ!")
      user_id = message.text.split(" ")[1]
      text = message.text.split(" ")[2]
      user = await client.get_users(user_id)
      
             
      button = [[ InlineKeyboardButton(text="Open Secret Message!", callback_data="whisper_data")]]
      whisper = f"""** 🕵 New Secret Message!**
      
**From User:** {mention}
**To UserID:** {user.mention}

**Note: this Message only can open the: To UserID
You are Not Allow To See Other Personal Messages!**
"""
      await client.send_message(message.chat.id,whisper,
               reply_markup=InlineKeyboardMarkup(button))
      bot_stats = await client.get_chat_member(message.chat.id, "self")
      if bot_stats.privileges:
            return await message.delete()

@Client.on_callback_query(filters.regex("whisper_data"))
async def whisperdata(_, query):
       if query.from_user.id == user.id:
          WHISPER = f"""{user.first_name}, here your message from {name} Message: {text}"""
          await query.answer(WHISPER, show_alert=True)
       else:
           await query.answer("YOUR NOT ALLOWED")
