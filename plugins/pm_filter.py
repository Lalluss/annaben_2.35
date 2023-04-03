# Kanged From @TroJanZheX
# Redirect added by @Joelkb
import asyncio
import re
import ast
import math
import random
import os

from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, SUPPORT_CHAT_ID, CUSTOM_FILE_CAPTION, MSG_ALRT, PICS, AUTH_GROUPS, P_TTI_SHOW_OFF, GRP_LNK, CHNL_LNK, NOR_IMG, LOG_CHANNEL, SPELL_IMG, MAX_B_TN, IMDB, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE, NO_RESULTS_MSG, FILE_CHANNEL_ID
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink
from database.users_chats_db import db
from filterdb import Media, get_file_details, get_search_results
from database.ia_filterdb import Media, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from database.gfilters_mdb import (
    find_gfilter,
    get_gfilters,
    del_allg
)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}

SPELL_MODE = True

SPELL_TXT = """➼ 𝑯𝒆𝒚 {mention}

➣ Title: {title}
➣ Genre: {genres}
➣ Year: {year}
➣ Rating: {rating}

𝙲𝙷𝙴𝙲𝙺 𝚃𝙷𝙴 𝙸𝙽𝚂𝚃𝚁𝚄𝙲𝚃𝙸𝙾𝙽𝚂

ᴄʟɪᴄᴋ ᴜʀ ᴄᴜʀʀᴇɴᴛ ʟᴀɴɢᴜᴀɢᴇ ʙᴜᴛᴛᴏɴ ᴀɴᴅ ᴄʜᴇᴄᴋ ᴛʜᴇ ɪɴꜱᴛʀᴜᴄᴛɪᴏɴꜱ 😌
"""
GTFL_TXT = """ HELLO
CLICK DOWNLOAD BUTTON """

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if message.chat.id != SUPPORT_CHAT_ID:
        await global_filters(client, message)
    manual = await manual_filters(client, message)
    if manual == False:
        settings = await get_settings(message.chat.id)
        try:
            if settings['auto_ffilter']:
                await auto_filter(client, message)
        except KeyError:
            grpid = await active_connection(str(message.from_user.id))
            await save_group_settings(grpid, 'auto_ffilter', True)
            settings = await get_settings(message.chat.id)
            if settings['auto_ffilter']:
                await auto_filter(client, message) 

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if content.startswith("/") or content.startswith("#"): return  # ignore commands and hashtags
    if user_id in ADMINS: return # ignore admins
    await message.reply_text("<b>⚠️ No need to send any message here.(ഇവിടെ ഒരു മെസ്സേജും അയക്കേണ്ടതില്ല). For Any Queries or Help (എന്തെങ്കിലും ചോദ്യങ്ങൾ അല്ലെങ്കിൽ സഹായത്തിന്).  😌 Contact: @lallu_tgs</b>")
    await bot.send_message(
        chat_id=LOG_CHANNEL,
        text=f"<b>#𝐏𝐌_𝐌𝐒𝐆\n\nNᴀᴍᴇ : {user}\n\nID : {user_id}\n\nMᴇssᴀɢᴇ : {content}</b>"
    )

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
        return

    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(query.message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    if ENABLE_SHORTLINK == True:
        if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    else:
        if settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'files#{file.file_id}'
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        callback_data=f'files_#{file.file_id}',
                    ),
                ]
                for file in files
            ]
    try:
        if settings['auto_delete']:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )

        else:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )
                
    except KeyError:
        grpid = await active_connection(str(query.message.from_user.id))
        await save_group_settings(grpid, 'auto_delete', True)
        settings = await get_settings(query.message.chat.id)
        if settings['auto_delete']:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )

        else:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )
    try:
        settings = await get_settings(query.message.chat.id)
        if settings['max_btn']:
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    except KeyError:
        await save_group_settings(query.message.chat.id, 'max_btn', False)
        settings = await get_settings(query.message.chat.id)
        if settings['max_btn']:
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    btn.insert(0, [
        InlineKeyboardButton("⚡ Cʜᴇᴄᴋ Bᴏᴛ PM ⚡", url=f"https://t.me/{temp.U_NAME}")
    ])
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[(int(movie_))]
    await query.answer(script.TOP_ALRT_MSG)
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            reqstr1 = query.from_user.id if query.from_user else 0
            reqstr = await bot.get_users(reqstr1)
            if NO_RESULTS_MSG:
                await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, movie)))
            k = await query.message.edit(script.MVE_NT_FND)
            await asyncio.sleep(10)
            await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "gfiltersdeleteallconfirm":
        await del_allg(query.message, 'gfilters')
        await query.answer("Done !")
        return
    elif query.data == "gfiltersdeleteallcancel": 
        await query.message.reply_to_message.delete()
        await query.message.delete()
        await query.answer("Process Cancelled !")
        return
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Mᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴘʀᴇsᴇɴᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ!!", quote=True)
                    return await query.answer(MSG_ALRT)
            else:
                await query.message.edit_text(
                    "I'ᴍ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ᴀɴʏ ɢʀᴏᴜᴘs!\nCʜᴇᴄᴋ /connections ᴏʀ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ᴀɴʏ ɢʀᴏᴜᴘs",
                    quote=True
                )
                return await query.answer(MSG_ALRT)

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer(MSG_ALRT)

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ Gʀᴏᴜᴘ Oᴡɴᴇʀ ᴏʀ ᴀɴ Aᴜᴛʜ Usᴇʀ ᴛᴏ ᴅᴏ ᴛʜᴀᴛ!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Tʜᴀᴛ's ɴᴏᴛ ғᴏʀ ʏᴏᴜ!!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Gʀᴏᴜᴘ Nᴀᴍᴇ : **{title}**\nGʀᴏᴜᴘ ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer(MSG_ALRT)
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Cᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer(MSG_ALRT)
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Dɪsᴄᴏɴɴᴇᴄᴛᴇᴅ ғʀᴏᴍ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴄᴏɴɴᴇᴄᴛɪᴏɴ !"
            )
        else:
            await query.message.edit_text(
                f"Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "Tʜᴇʀᴇ ᴀʀᴇ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴs!! Cᴏɴɴᴇᴄᴛ ᴛᴏ sᴏᴍᴇ ɢʀᴏᴜᴘs ғɪʀsᴛ.",
            )
            return await query.answer(MSG_ALRT)
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Yᴏᴜʀ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɢʀᴏᴜᴘ ᴅᴇᴛᴀɪʟs ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "gfilteralert" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_gfilter('gfilters', keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        clicked = query.from_user.id
        try:
            typed = query.message.reply_to_message.from_user.id
        except:
            typed = query.from_user.id
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                if clicked == typed:
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(f"Hᴇʏ {query.from_user.first_name}, Tʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ. Rᴇǫᴜᴇsᴛ Yᴏᴜʀ's !", show_alert=True)
            elif settings['botpm']:
                if clicked == typed:
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(f"Hᴇʏ {query.from_user.first_name}, Tʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ. Rᴇǫᴜᴇsᴛ Yᴏᴜʀ's !", show_alert=True)
            else:
                if clicked == typed:
                    joelkb_creatorbeatz = await client.send_cached_media(
                        chat_id=int(FILE_CHANNEL_ID),
                        file_id=file_id,
                        caption=f_caption,
                        protect_content=True if ident == "filep" else False,
                        reply_markup=InlineKeyboardMarkup(
                            [
                             [
                              InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                              InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                           ],[
                              InlineKeyboardButton("Bᴏᴛ Oᴡɴᴇʀ", url="t.me/Lallu_tgs")
                             ]
                            ]
                        )
                    )
                    joelkb_msg = await query.message.reply_text(
                        text=script.FILE_MSG.format(query.from_user.mention, title, size),                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=InlineKeyboardMarkup(
                            [[
                                InlineKeyboardButton("📁ɢᴇᴛ ꜰɪʟᴇ📁", url=joelkb_creatorbeatz.link)
                            ],[
                                InlineKeyboardButton("📥ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ📥", url='https://t.me/databut')
                            ]]
                        )
                    )
                    await asyncio.sleep(600)
                    await joelkb_creatorbeatz.delete()
                    await joelkb_msg.delete()
                else:
                    await query.answer(f"Hᴇʏ {query.from_user.first_name}, Tʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ. Rᴇǫᴜᴇsᴛ Yᴏᴜʀ's !", show_alert=True)
                await query.answer('Check PM, I have sent files in pm',show_alert = True)
        except UserIsBlocked:
            await query.answer('Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("Jᴏɪɴ ᴏᴜʀ Bᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟ ᴍᴀʜɴ! 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                  InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                  InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
               ],[
                  InlineKeyboardButton("Bᴏᴛ Oᴡɴᴇʀ", url="t.me/creatorbeatz")
                 ]
                ]
            )
        )
    elif query.data == "pages":
        await query.answer()

    elif query.data.startswith("opnsetgrp"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Fɪʟᴛᴇʀ Bᴜᴛᴛᴏɴ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Sɪɴɢʟᴇ' if settings["button"] else 'Dᴏᴜʙʟᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Fɪʟᴇ Sᴇɴᴅ Mᴏᴅᴇ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Mᴀɴᴜᴀʟ Sᴛᴀʀᴛ' if settings["botpm"] else 'ᴄʜᴀɴɴᴇʟ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Fɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ShortLink',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML
            )
            await query.message.edit_reply_markup(reply_markup)
        
    elif query.data.startswith("opnsetpm"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Tʜᴇ Rɪɢʜᴛs Tᴏ Dᴏ Tʜɪs !", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        btn2 = [[
                 InlineKeyboardButton("Cʜᴇᴄᴋ PM", url=f"t.me/{temp.U_NAME}")
               ]]
        reply_markup = InlineKeyboardMarkup(btn2)
        await query.message.edit_text(f"<b>Yᴏᴜʀ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ ғᴏʀ {title} ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ʏᴏᴜʀ PM</b>")
        await query.message.edit_reply_markup(reply_markup)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Fɪʟᴛᴇʀ Bᴜᴛᴛᴏɴ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Sɪɴɢʟᴇ' if settings["button"] else 'Dᴏᴜʙʟᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Fɪʟᴇ Sᴇɴᴅ Mᴏᴅᴇ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Mᴀɴᴜᴀʟ Sᴛᴀʀᴛ' if settings["botpm"] else 'Aᴜᴛᴏ Sᴇɴᴅ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Fɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ShortLink',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await client.send_message(
                chat_id=userid,
                text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=query.message.id
            )

    elif query.data.startswith("show_option"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("Uɴᴀᴠᴀɪʟᴀʙʟᴇ", callback_data=f"unavailable#{from_user}"),
                InlineKeyboardButton("Uᴘʟᴏᴀᴅᴇᴅ", callback_data=f"uploaded#{from_user}")
             ],[
                InlineKeyboardButton("Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ", callback_data=f"already_available#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Hᴇʀᴇ ᴀʀᴇ ᴛʜᴇ ᴏᴘᴛɪᴏɴs !")
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)
        
    elif query.data.startswith("unavailable"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("⚠️ Uɴᴀᴠᴀɪʟᴀʙʟᴇ ⚠️", callback_data=f"unalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Uɴᴀᴠᴀɪʟᴀʙʟᴇ !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Sᴏʀʀʏ Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Sᴏʀʀʏ Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("uploaded"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("✅ Uᴘʟᴏᴀᴅᴇᴅ ✅", callback_data=f"upalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Uᴘʟᴏᴀᴅᴇᴅ !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("already_available"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("🟢 Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ 🟢", callback_data=f"alalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton("Vɪᴇᴡ Sᴛᴀᴛᴜs", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴏᴜʀ ʙᴏᴛ's ᴅᴀᴛᴀʙᴀsᴇ. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴏᴜʀ ʙᴏᴛ's ᴅᴀᴛᴀʙᴀsᴇ. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("alalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ !", show_alert=True)
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("upalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Uᴘʟᴏᴀᴅᴇᴅ !", show_alert=True)
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)
        
    elif query.data.startswith("unalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Uɴᴀᴠᴀɪʟᴀʙʟᴇ !", show_alert=True)
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data == "reqinfo":
        await query.answer(text=script.REQINFO, show_alert=True)

    elif query.data == "minfo":
        await query.answer(text=script.MINFO, show_alert=True)

    elif query.data == "sinfo":
        await query.answer(text=script.SINFO, show_alert=True)

    elif query.data == "start":
        await query.message.delete()
        buttons = [[
                    InlineKeyboardButton('🔮𝚂𝙴𝙻𝙴𝙲𝚃 𝚄𝚁 𝙻𝙰𝙽𝙶🔮', callback_data='lang')
                ],[
                    InlineKeyboardButton('𝙼𝙰𝙻', callback_data='smal'),
                    InlineKeyboardButton('𝙷𝙸𝙽', callback_data='shin'),
                    InlineKeyboardButton('𝚃𝙰𝙼', callback_data='stam'),
                    InlineKeyboardButton('𝙴𝙽𝙶', callback_data='seng')
                ],[
                    InlineKeyboardButton('☺️ 𝚃𝙷𝙰𝙽𝙺 𝚄 ☺️', callback_data='thank')
                  ]]
      
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer(MSG_ALRT)

    elif query.data == "smal":
        buttons = [[
            InlineKeyboardButton('𝙰𝙳𝙳 𝙼𝙴 𝚃𝙾 𝚄𝚁 𝙶𝚁𝙿', url=f'https://t.me/{temp.U_NAME}?startgroup=true')
        ],[
            InlineKeyboardButton('𝙼𝚈 𝙳𝙴𝚅', url=f'http://t.me/Lallu_tgs'),
            InlineKeyboardButton('𝙼𝚈 𝙶𝚁𝙾𝚄𝙿', url=f'https://t.me/EDIT_REPO')
        ],[
            InlineKeyboardButton('𝙲𝙷𝙴𝙲𝙺', callback_data='help'),
            InlineKeyboardButton('𝙳𝙰𝚃𝙰𝚂', callback_data='about'),
            InlineKeyboardButton('𝙸𝙽𝙻𝙸𝙽𝙴', switch_inline_query_current_chat='')
        ],[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='thank')
        ]]

        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SMAL_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "shin":
        buttons = [[
            InlineKeyboardButton('𝙰𝙳𝙳 𝙼𝙴 𝚃𝙾 𝚄𝚁 𝙶𝚁𝙿', url=f'https://t.me/{temp.U_NAME}?startgroup=true')
        ],[
            InlineKeyboardButton('𝙼𝚈 𝙳𝙴𝚅', url=f'http://t.me/Lallu_tgs'),
            InlineKeyboardButton('𝙼𝚈 𝙶𝚁𝙾𝚄𝙿', url=f'https://t.me/EDIT_REPO')
        ],[
            InlineKeyboardButton('𝙲𝙷𝙴𝙲𝙺', callback_data='help'),
            InlineKeyboardButton('𝙳𝙰𝚃𝙰𝚂', callback_data='about'),
            InlineKeyboardButton('𝙸𝙽𝙻𝙸𝙽𝙴', switch_inline_query_current_chat='')
        ],[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='thank')
        ]]

        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SHIN_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "seng":
        buttons = [[
            InlineKeyboardButton('𝙰𝙳𝙳 𝙼𝙴 𝚃𝙾 𝚄𝚁 𝙶𝚁𝙿', url=f'https://t.me/{temp.U_NAME}?startgroup=true')
        ],[
            InlineKeyboardButton('𝙼𝚈 𝙳𝙴𝚅', url=f'http://t.me/Lallu_tgs'),
            InlineKeyboardButton('𝙼𝚈 𝙶𝚁𝙾𝚄𝙿', url=f'https://t.me/EDIT_REPO')
        ],[
            InlineKeyboardButton('𝙲𝙷𝙴𝙲𝙺', callback_data='help'),
            InlineKeyboardButton('𝙳𝙰𝚃𝙰𝚂', callback_data='about'),
            InlineKeyboardButton('𝙸𝙽𝙻𝙸𝙽𝙴', switch_inline_query_current_chat='')
        ],[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='thank')
        ]]

        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SENG_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "stam":
        buttons = [[
            InlineKeyboardButton('𝙰𝙳𝙳 𝙼𝙴 𝚃𝙾 𝚄𝚁 𝙶𝚁𝙿', url=f'https://t.me/{temp.U_NAME}?startgroup=true')
        ],[
            InlineKeyboardButton('𝙼𝚈 𝙳𝙴𝚅', url=f'http://t.me/Lallu_tgs'),
            InlineKeyboardButton('𝙼𝚈 𝙶𝚁𝙾𝚄𝙿', url=f'https://t.me/EDIT_REPO')
        ],[
            InlineKeyboardButton('𝙲𝙷𝙴𝙲𝙺', callback_data='help'),
            InlineKeyboardButton('𝙳𝙰𝚃𝙰𝚂', callback_data='about'),
            InlineKeyboardButton('𝙸𝙽𝙻𝙸𝙽𝙴', switch_inline_query_current_chat='')
        ],[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='thank')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.STAM_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "filters":
        await query.message.delete()
        buttons = [[
            InlineKeyboardButton('Mᴀɴᴜᴀʟ FIʟᴛᴇʀ', callback_data='manuelfilter'),
            InlineKeyboardButton('Aᴜᴛᴏ FIʟᴛᴇʀ', callback_data='autofilter')
        ],[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Gʟᴏʙᴀʟ Fɪʟᴛᴇʀs', callback_data='global_filters')
        ]]  
     
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            text=script.ALL_FILTERS.format(query.from_user.mention),
            chat_id=query.message.chat.id,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "global_filters":
        await query.message.delete()
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='filters')
        ]]

        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            text=script.GFILTER_TXT.format(query.from_user.mention),
            chat_id=query.message.chat.id,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )    
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('FIʟᴛᴇʀs', callback_data='filters'),
            InlineKeyboardButton('Fɪʟᴇ Sᴛᴏʀᴇ', callback_data='store_file')
        ], [
            InlineKeyboardButton('Cᴏɴɴᴇᴄᴛɪᴏɴ', callback_data='coct'),
            InlineKeyboardButton('Exᴛʀᴀ Mᴏᴅs', callback_data='extra')
        ], [
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='thank'),
            InlineKeyboardButton('Sᴛᴀᴛᴜs', callback_data='stats')
        ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        await query.message.delete()
        buttons = [[
            InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
            InlineKeyboardButton('Sᴏᴜʀᴄᴇ Cᴏᴅᴇ', callback_data='source')
        ],[
            InlineKeyboardButton('𝙱𝙰𝙲𝙺', callback_data='thank'),
            InlineKeyboardButton('Cʟᴏsᴇ', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            text=script.ABOUT_TXT.format(query.from_user.mention),
            chat_id=query.message.chat.id,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "lang":
        await query.message.delete()
        buttons = [[
                    InlineKeyboardButton('🔮𝚂𝙴𝙻𝙴𝙲𝚃 𝚄𝚁 𝙻𝙰𝙽𝙶🔮', callback_data='lang')
                ],[
                    InlineKeyboardButton('𝙼𝙰𝙻', callback_data='smal'),
                    InlineKeyboardButton('𝙷𝙸𝙽', callback_data='shin'),
                    InlineKeyboardButton('𝚃𝙰𝙼', callback_data='stam'),
                    InlineKeyboardButton('𝙴𝙽𝙶', callback_data='seng')
                ],[
                    InlineKeyboardButton('☺️ 𝚃𝙷𝙰𝙽𝙺 𝚄 ☺️', callback_data='thank')
                  ]]
      
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            text=script.START_TXT.format(query.from_user.mention),
            chat_id=query.message.chat.id,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "thank":
        await query.message.delete()
        buttons = [[
            InlineKeyboardButton('𝙰𝙳𝙳 𝙼𝙴', url=f'https://t.me/{temp.U_NAME}?startgroup=true'),
        ],[
            InlineKeyboardButton('𝚂𝚃𝙰𝚁𝚃 𝙼𝚂𝙶', callback_data='astart'),
            InlineKeyboardButton('𝚌𝚕𝚘𝚜𝚎', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            text=script.THANK_TXT.format(query.from_user.mention),
            chat_id=query.message.chat.id,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "astart":
        await query.message.delete()
        buttons = [[
            InlineKeyboardButton('𝚂𝚃𝙰𝚁𝚃', callback_data='lang'),
            InlineKeyboardButton('𝙲𝙻𝙾𝚂𝙴', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            text=script.ASTART_TXT.format(query.from_user.mention),
            chat_id=query.message.chat.id,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "source":
        await query.message.delete()
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            text=script.SOURCE_TXT.format(query.from_user.mention),
            chat_id=query.message.chat.id,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "manuelfilter":
        await query.message.delete()
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='filters'),
            InlineKeyboardButton('Bᴜᴛᴛᴏɴs', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            text=script.MANUELFILTER_TXT.format(query.from_user.mention),
            chat_id=query.message.chat.id,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "button":
        await query.message.delete()
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            text=script.BUTTON_TXT.format(query.from_user.mention),
            chat_id=query.message.chat.id,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "autofilter":
        await query.message.delete()
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='filters')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            text=script.AUTOFILTER_TXT.format(query.from_user.mention),
            chat_id=query.message.chat.id,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "coct":
        await query.message.delete()
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            text=script.CONNECTION_TXT.format(query.from_user.mention),
            chat_id=query.message.chat.id,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        await query.message.delete()
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Aᴅᴍɪɴ', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            text=script.EXTRAMOD_TXT.format(query.from_user.mention),
            chat_id=query.message.chat.id,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )    
    elif query.data == "store_file":
        await query.message.delete()
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.send_message(
            text=script.FILE_STORE_TXT.format(query.from_user.mention),
            chat_id=query.message.chat.id,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "gtfl":
        buttons = [[
            InlineKeyboardButton('DOWNLOAD', url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}"))
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=GTFL_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "mal":
        buttons = [[
            InlineKeyboardButton('SEARCH', url='https://google.com/find?q={reply}')
        ],[
            InlineKeyboardButton('Cʟᴏsᴇ', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MAL_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "eng":
        buttons = [[
            InlineKeyboardButton('SEARCH', url='https://google.com/find?q={reply}')
        ],[
            InlineKeyboardButton('Cʟᴏsᴇ', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ENG_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "bet":
        buttons = [[
            InlineKeyboardButton('SEARCH', url='https://google.com/find?q={reply}')
        ],[
            InlineKeyboardButton('Cʟᴏsᴇ', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HIN_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "tam":
        buttons = [[
            InlineKeyboardButton('SEARCH', url='https://google.com/find?q={reply}')
        ],[
            InlineKeyboardButton('Cʟᴏsᴇ', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.TAM_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "admin":
        await query.message.delete()
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='extra')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('⟲ Rᴇғʀᴇsʜ', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('⟲ Rᴇғʀᴇsʜ', callback_data='rfrsh')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "owner_info":
            btn = [[
                    InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="start"),
                    InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="t.me/creatorbeatz")
                  ]]
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_text(
                text=(script.OWNER_INFO),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )

    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Yᴏᴜʀ Aᴄᴛɪᴠᴇ Cᴏɴɴᴇᴄᴛɪᴏɴ Hᴀs Bᴇᴇɴ Cʜᴀɴɢᴇᴅ. Gᴏ Tᴏ /connections ᴀɴᴅ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴ.")
            return await query.answer(MSG_ALRT)

        if set_type == 'is_shortlink' and query.from_user.id not in ADMINS:
            return await query.answer(text=f"Hey {query.from_user.first_name}, You can't change shortlink settings for your group !\n\nIt's an admin only setting !", show_alert=True)

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Fɪʟᴛᴇʀ Bᴜᴛᴛᴏɴ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Sɪɴɢʟᴇ' if settings["button"] else 'Dᴏᴜʙʟᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Fɪʟᴇ Sᴇɴᴅ Mᴏᴅᴇ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Mᴀɴᴜᴀʟ Sᴛᴀʀᴛ' if settings["botpm"] else 'Aᴜᴛᴏ Sᴇɴᴅ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Iᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Msɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aᴜᴛᴏ-Fɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Mᴀx Bᴜᴛᴛᴏɴs',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ShortLink',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer(MSG_ALRT)

    
async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(message.chat.id, search.lower(), offset=0, filter=True)
            if not files:
                if SPELL_MODE:  
                    reply = search.replace(" ", "+")
                    reply_markup = InlineKeyboardMarkup([[
                        InlineKeyboardButton("📁𝙸𝙽𝚂𝚃𝚁𝚄𝙲𝚃𝙸𝙾𝙽𝚂📁", callback_data="instr")
                    ],[
                        InlineKeyboardButton("ᴍᴀʟ", callback_data="mal"),
                        InlineKeyboardButton("ᴛᴀᴍ", callback_data="tam"),
                        InlineKeyboardButton("ʜɪɴ", callback_data="bet"),
                        InlineKeyboardButton("ᴇɴɢ", callback_data="eng")
                    ],[
                        InlineKeyboardButton("🔮ɪᴍᴅ🔮", url=f"https://imdb.com/find?q={reply}")
                    ]])
                        await message.reply_photo(photo=(SPELL_IMG), text=SPELL_TXT.format(mention=message.from_user.mention, query=search, title=imdb.get('title'), genres=imdb.get('genres'), year=imdb.get('year'), rating=imdb.get('rating'), short=imdb.get('short_info'), url=imdb['url']), reply_markup=reply_markup)
                        return
                    else:
                        return
                else:
                    return
        else:
            return
    else:
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    settings = await get_settings(message.chat.id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    pre = 'filep' if settings['file_secure'] else 'file'
    if ENABLE_SHORTLINK == True:
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
    else:
        if settings["button"]:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'{pre}#{file.file_id}'
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        callback_data=f'{pre}#{file.file_id}',
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        callback_data=f'{pre}#{file.file_id}',
                    ),
                ]
                for file in files
            ]

    try:
        if settings['auto_delete']:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )

        else:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )
                
    except KeyError:
        grpid = await active_connection(str(message.from_user.id))
        await save_group_settings(grpid, 'auto_delete', True)
        settings = await get_settings(message.chat.id)
        if settings['auto_delete']:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ɪɴꜰᴏ', 'reqinfo'),
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )

        else:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'ᴍᴏᴠɪᴇ', 'minfo'),
                    InlineKeyboardButton(f'ꜱᴇʀɪᴇꜱ', 'sinfo')
                ]
            )

    btn.insert(0, [
        InlineKeyboardButton("⚡ Cʜᴇᴄᴋ Bᴏᴛ PM ⚡", url=f"https://t.me/{temp.U_NAME}")
    ])

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        try:
            settings = await get_settings(message.chat.id)
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
            else:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(message.chat.id, 'max_btn', False)
            settings = await get_settings(message.chat.id)
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
            else:
                btn.append(
                    [InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
    else:
        btn.append(
            [InlineKeyboardButton(text="𝐍𝐎 𝐌𝐎𝐑𝐄 𝐏𝐀𝐆𝐄𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄",callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"<b>Hᴇʏ {message.from_user.mention}, Hᴇʀᴇ ɪs Wʜᴀᴛ I Fᴏᴜɴᴅ Iɴ Mʏ Dᴀᴛᴀʙᴀsᴇ Fᴏʀ Yᴏᴜʀ Qᴜᴇʀʏ {search}.</b>"
    if imdb and imdb.get('poster'):
        try:
            if message.chat.id == SUPPORT_CHAT_ID:
                await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. Kɪɴᴅʟʏ ᴜsᴇ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴏʀ ᴍᴀᴋᴇ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴍᴏᴠɪᴇ ғɪʟᴇs. Tʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...\n\nFᴏʀ Mᴏᴠɪᴇs, Jᴏɪɴ @free_movies_all_languages</b>")
            else:
                hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hehe.delete()
                        await message.delete()
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, 'auto_delete', True)
                    settings = await get_settings(message.chat.id)
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hehe.delete()
                        await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            if message.chat.id == SUPPORT_CHAT_ID:
                await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. Kɪɴᴅʟʏ ᴜsᴇ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴏʀ ᴍᴀᴋᴇ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴍᴏᴠɪᴇ ғɪʟᴇs. Tʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...\n\nFᴏʀ Mᴏᴠɪᴇs, Jᴏɪɴ @free_movies_all_languages</b>")
            else:
                pic = imdb.get('poster')
                poster = pic.replace('.jpg', "._V1_UX360.jpg")
                hmm = await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hmm.delete()
                        await message.delete()
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, 'auto_delete', True)
                    settings = await get_settings(message.chat.id)
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await hmm.delete()
                        await message.delete()
        except Exception as e:
            if message.chat.id == SUPPORT_CHAT_ID:
                await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. Kɪɴᴅʟʏ ᴜsᴇ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴏʀ ᴍᴀᴋᴇ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴍᴏᴠɪᴇ ғɪʟᴇs. Tʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...\n\nFᴏʀ Mᴏᴠɪᴇs, Jᴏɪɴ @free_movies_all_languages</b>")
            else:
                logger.exception(e)
                fek = await message.reply_photo(photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
                try:
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await fek.delete()
                        await message.delete()
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, 'auto_delete', True)
                    settings = await get_settings(message.chat.id)
                    if settings['auto_delete']:
                        await asyncio.sleep(600)
                        await fek.delete()
                        await message.delete()
    else:
        if message.chat.id == SUPPORT_CHAT_ID:
            await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. Kɪɴᴅʟʏ ᴜsᴇ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴏʀ ᴍᴀᴋᴇ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴍᴏᴠɪᴇ ғɪʟᴇs. Tʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...\n\nFᴏʀ Mᴏᴠɪᴇs, Jᴏɪɴ @free_movies_all_languages</b>")
        else:
            fuk = await message.reply_photo(photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await fuk.delete()
                    await message.delete()
            except KeyError:
                grpid = await active_connection(str(message.from_user.id))
                await save_group_settings(grpid, 'auto_delete', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await fuk.delete()
                    await message.delete()
    if spoll:
        await msg.message.delete()

async def manual_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            try:
                                if settings['auto_delete']:
                                    await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await joelkb.delete()

                        else:
                            button = eval(btn)
                            hmm = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                            try:
                                if settings['auto_delete']:
                                    await hmm.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await hmm.delete()

                    elif btn == "[]":
                        oto = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            protect_content=True if settings["file_secure"] else False,
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        try:
                            if settings['auto_delete']:
                                await oto.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_delete', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_delete']:
                                await oto.delete()

                    else:
                        button = eval(btn)
                        dlt = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                        try:
                            if settings['auto_delete']:
                                await dlt.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_delete', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_delete']:
                                await dlt.delete()

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False

async def global_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            
                        else:
                            button = eval(btn)
                            hmm = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )

                    elif btn == "[]":
                        oto = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )

                    else:
                        button = eval(btn)
                        dlt = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
