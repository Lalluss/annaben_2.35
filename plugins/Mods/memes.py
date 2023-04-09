#created @lallu_tg


from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters
from requests import get
import random
import requests 
import secureme

reactions = [
    "( ͡° ͜ʖ ͡°)", "( . •́ _ʖ •̀ .)", "( ಠ ͜ʖ ಠ)", "( ͡ ͜ʖ ͡ )", "(ʘ ͜ʖ ʘ)",
    "ヾ(´〇`)ﾉ♪♪♪", "ヽ(o´∀`)ﾉ♪♬", "♪♬((d⌒ω⌒b))♬♪", "└(＾＾)┐", "(￣▽￣)/♫•*¨*•.¸¸♪",
    "ヾ(⌐■_■)ノ♪", "乁( • ω •乁)", "♬♫♪◖(● o ●)◗♪♫♬", "(っ˘ڡ˘ς)", "( ˘▽˘)っ♨",
    "(　・ω・)⊃-[二二]", "(*´ー`)旦 旦(￣ω￣*)", "( ￣▽￣)[] [](≧▽≦ )", "(*￣▽￣)旦 且(´∀`*)",
    "(ノ ˘_˘)ノ　ζ|||ζ　ζ|||ζ　ζ|||ζ", "(ノ°∀°)ノ⌒･*:.｡. .｡.:*･゜ﾟ･*☆",
    "(⊃｡•́‿•̀｡)⊃━✿✿✿✿✿✿", "(∩` ﾛ ´)⊃━炎炎炎炎炎", "( ・∀・)・・・--------☆",
    "( -ω-)／占~~~~~", "○∞∞∞∞ヽ(^ー^ )", "(*＾＾)/~~~~~~~~~~◎", "((( ￣□)_／",
    "(ﾒ￣▽￣)︻┳═一", "ヽ( ･∀･)ﾉ_θ彡☆Σ(ノ `Д´)ノ", "(*`0´)θ☆(メ°皿°)ﾉ",
    "(; -_-)――――――C<―_-)", "ヽ(>_<ヽ) ―⊂|=0ヘ(^‿^ )", "(҂` ﾛ ´)︻デ═一 ＼(º □ º l|l)/",
    "/( .□.)＼ ︵╰(°益°)╯︵ /(.□. /)", "(`⌒*)O-(`⌒´Q)", "(っ•﹏•)っ ✴==≡눈٩(`皿´҂)ง",
    "ヾ(・ω・)メ(・ω・)ノ", "(*^ω^)八(⌒▽⌒)八(-‿‿- )ヽ", "ヽ( ⌒ω⌒)人(=^‥^= )ﾉ",
    "｡*:☆(・ω・人・ω・)｡:゜☆｡", "(°(°ω(°ω°(☆ω☆)°ω°)ω°)°)", "(っ˘▽˘)(˘▽˘)˘▽˘ς)",
    "(*＾ω＾)人(＾ω＾*)", "＼(▽￣ \ (￣▽￣) / ￣▽)／", "(￣Θ￣)", "＼( ˋ Θ ´ )／",
    "( ´(00)ˋ )", "＼(￣(oo)￣)／", "／(≧ x ≦)＼", "／(=･ x ･=)＼", "(=^･ω･^=)",
    "(= ; ｪ ; =)", "(=⌒‿‿⌒=)", "(＾• ω •＾)", "ଲ(ⓛ ω ⓛ)ଲ", "ଲ(ⓛ ω ⓛ)ଲ", "(^◔ᴥ◔^)",
    "[(－－)]..zzZ", "(￣o￣) zzZZzzZZ", "(＿ ＿*) Z z z", "☆ﾐ(o*･ω･)ﾉ",
    "ε=ε=ε=ε=┌(;￣▽￣)┘", "ε===(っ≧ω≦)っ", "__φ(．．)", "ヾ( `ー´)シφ__", "( ^▽^)ψ__",
    "|･ω･)", "|д･)", "┬┴┬┴┤･ω･)ﾉ", "|･д･)ﾉ", "(*￣ii￣)", "(＾〃＾)", "m(_ _)m",
    "人(_ _*)", "(シ. .)シ", "(^_~)", "(>ω^)", "(^_<)〜☆", "(^_<)", "(づ￣ ³￣)づ",
    "(⊃｡•́‿•̀｡)⊃", "⊂(´• ω •`⊂)", "(*・ω・)ﾉ", "(^-^*)/", "ヾ(*'▽'*)", "(^０^)ノ",
    "(*°ｰ°)ﾉ", "(￣ω￣)/", "(≧▽≦)/", "w(°ｏ°)w", "(⊙_⊙)", "(°ロ°) !", "∑(O_O;)",
    "(￢_￢)", "(¬_¬ )", "(↼_↼)", "(￣ω￣;)", "┐('～`;)┌", "(・_・;)", "(＠_＠)",
    "(•ิ_•ิ)?", "ヽ(ー_ー )ノ", "┐(￣ヘ￣)┌", "┐(￣～￣)┌", "┐( ´ д ` )┌", "╮(︶▽︶)╭",
    "ᕕ( ᐛ )ᕗ", "(ノωヽ)", "(″ロ゛)", "(/ω＼)", "(((＞＜)))", "~(>_<~)", "(×_×)",
    "(×﹏×)", "(ノ_<。)", "(μ_μ)", "o(TヘTo)", "( ﾟ，_ゝ｀)", "( ╥ω╥ )", "(／ˍ・、)",
    "(つω`｡)", "(T_T)", "o(〒﹏〒)o", "(＃`Д´)", "(・`ω´・)", "( `ε´ )", "(ﾒ` ﾛ ´)",
    "Σ(▼□▼メ)", "(҂ `з´ )", "٩(╬ʘ益ʘ╬)۶", "↑_(ΦwΦ)Ψ", "(ﾉಥ益ಥ)ﾉ", "(＃＞＜)",
    "(；￣Д￣)", "(￢_￢;)", "(＾＾＃)", "(￣︿￣)", "ヾ( ￣O￣)ツ", "(ᗒᗣᗕ)՞",
    "(ノ_<。)ヾ(´ ▽ ` )", "ヽ(￣ω￣(。。 )ゝ", "(ﾉ_；)ヾ(´ ∀ ` )", "(´-ω-`( _ _ )",
    "(⌒_⌒;)", "(*/_＼)", "( ◡‿◡ *)", "(//ω//)", "(￣▽￣*)ゞ", "(„ಡωಡ„)",
    "(ﾉ´ з `)ノ", "(♡-_-♡)", "(─‿‿─)♡", "(´ ω `♡)", "(ღ˘⌣˘ღ)", "(´• ω •`) ♡",
    "╰(*´︶`*)╯♡", "(≧◡≦) ♡", "♡ (˘▽˘>ԅ( ˘⌣˘)", "σ(≧ε≦σ) ♡", "(˘∀˘)/(μ‿μ) ❤",
    "Σ>―(〃°ω°〃)♡→", "(* ^ ω ^)", "(o^▽^o)", "ヽ(・∀・)ﾉ", "(o･ω･o)", "(^人^)",
    "( ´ ω ` )", "(´• ω •`)", "╰(▔∀▔)╯", "(✯◡✯)", "(⌒‿⌒)", "(*°▽°*)",
    "(´｡• ᵕ •｡`)", "ヽ(>∀<☆)ノ", "＼(￣▽￣)／", "(o˘◡˘o)", "(╯✧▽✧)╯", "( ‾́ ◡ ‾́ )",
    "(๑˘︶˘๑)", "(´･ᴗ･ ` )", "( ͡° ʖ̯ ͡°)", "( ఠ ͟ʖ ఠ)", "( ಥ ʖ̯ ಥ)", "(≖ ͜ʖ≖)",
    "ヘ(￣ω￣ヘ)", "(ﾉ≧∀≦)ﾉ", "└(￣-￣└))", "┌(＾＾)┘", "(^_^♪)", "(〜￣△￣)〜",
    "(｢• ω •)｢", "( ˘ ɜ˘) ♬♪♫", "( o˘◡˘o) ┌iii┐", "♨o(>_<)o♨",
    "( ・・)つ―{}@{}@{}-", "(*´з`)口ﾟ｡ﾟ口(・∀・ )", "( *^^)o∀*∀o(^^* )", "-●●●-ｃ(・・ )",
    "(ﾉ≧∀≦)ﾉ ‥…━━━★", "╰( ͡° ͜ʖ ͡° )つ──☆*:・ﾟ", "(∩ᄑ_ᄑ)⊃━☆ﾟ*･｡*･:≡( ε:)"
]

@Client.on_message(filters.command("react"))
async def react(_, m):
         react = random.choice(reactions)
         if m.reply_to_message:
               await m.reply_to_message.reply_text(react)
         else:
                await m.reply_text(react)
     

@Client.on_message(filters.command(["encrypt","hide"]))
async def encrypt(_, m):
           reply = m.reply_to_message
           if not reply:
                return await m.reply_text("reply to message encrypt")
           if reply:
                   rtext = m.reply_to_message.text
                   encrypt = secureme.encrypt(rtext)
                   text = await m.reply_text("encrypting....")
                   await text.edit(encrypt)

@Client.on_message(filters.command(["decrypt","show"]))
async def decrypt(_, m):
           reply = m.reply_to_message
           if not reply:
                return await m.reply_text("reply to message decrypt")
           if reply:
                   rtext = m.reply_to_message.text
                   decrypt = secureme.decrypt(rtext)
                   text = await m.reply_text("decrypting....")
                   await text.edit(decrypt)

@Client.on_message(filters.regex("good morning|goodmorning"))
def gm(_, m: Message):
    reply = m.reply_to_message
    if reply:
        m.reply_to_message.reply_text(f"good morning! {reply.from_user.mention}")
    else:
        m.reply(f"good morning! {m.from_user.mention}")
 

@Client.on_message(filters.regex("good night|goodnight"))
def gn(_, m: Message):
    reply = m.reply_to_message
    if reply:
        api = requests.get("https://nekos.best/api/v2/sleep").json()
        url = api["results"][0]['url']
        m.reply_to_message.reply_animation(url, caption=f"good night! {reply.from_user.mention}")
    else:
        api = requests.get("https://nekos.best/api/v2/sleep").json()
        url = api["results"][0]['url']
        m.reply_animation(url,caption=f"good night! {m.from_user.mention}")
    
gbam_text = """
#GBANNED
**Froma Chat:** @{}
**Admin:** {}
**User :** {}
**Reason:** `{}`
**Chat Count:** `{}`
"""


gban_img = "https://telegra.ph/file/0a0657d58149b982efcd0.jpg"

@Client.on_message(filters.command(["gban", "gbam"]))
async def gbams(_, m: Message):
      reply = m.reply_to_message
      if not reply:
       return await m.reply("reply someone:\n/gban or /gbam")
      if len(m.command) < 2:
          return await m.reply("add a reason to gban")
      if reply.from_user.id == BOT_ID:
          return await m.reply_text("nigga I can't gban myself")
      if reply:
          user1 = m.from_user
          reason = m.text.split(None, 1)[1]
          count = random.randint(10,30)
          user2 = reply.from_user
          chat = m.chat
          gbam = await m.reply_photo(gban_img,caption="Gbaning...")
          await gbam.edit_caption(gbam_text.format(chat.username,user1.mention,
                                            user2.mention,reason,count))
       
      
@Client.on_message(filters.command("joke"))
def joke(_, message: Message):
        res = requests.get('https://some-random-api.ml/joke').json()
        text = res['joke']
        message.reply_text(text)
        
@Client.on_message(filters.command("catfact"))
async def catfacts(_, m):
          api = get("https://cat-fact.herokuapp.com/facts/random").json()
          await m.reply_text(api["text"])
               
@Client.on_message(filters.command("animalfact"))
async def animals(_, m):
          api = get("https://axoltlapi.herokuapp.com/").json()
          await m.reply_photo(
        api["url"], caption=api["facts"])
            
@Client.on_message(filters.command("dogfact"))
async def dogfacts(_, m):
          api = get("https://dog-facts-api.herokuapp.com/api/v1/resources/dogs?number=1").json()
          await m.reply_text(api[0]["fact"])
               
