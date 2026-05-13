import os
import random
import string
import time
import asyncio
import json
import logging

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)
from telegram.constants import ChatType, ParseMode

from database import (
    init_db, get_user, update_user, get_all_users, get_top_rich, get_top_kills,
    get_global_rank, save_code, use_code, get_group, save_group,
    get_warnings, add_warning, remove_warning, update_bomb_score,
    get_bomb_leaders, get_bomb_rank, save_chat
)
if not os.environ.get('ORACLE_DEPLOY'):
    from keep_alive import keep_alive

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8601344819:AAE1nBCUJt74qq3i44Dl0l4r4_SBzcN0VIc"

OWNERS = ['light_speedy', 'alenachistyakova_m', 'speedy_fighter', 'its_aanya_07']

GIFT_ITEMS = {
    'rose':       {'emoji': '🌹', 'price': 500,  'name': 'Rᴏꜱᴇ'},
    'chocolate':  {'emoji': '🍫', 'price': 800,  'name': 'Cʜᴏᴄᴏʟᴀᴛᴇ'},
    'ring':       {'emoji': '💍', 'price': 2000, 'name': 'Rɪɴɢ'},
    'teddy':      {'emoji': '🧸', 'price': 1500, 'name': 'Tᴇᴅᴅʏ Bᴇᴀʀ'},
    'pizza':      {'emoji': '🍕', 'price': 600,  'name': 'Pɪᴢᴢᴀ'},
    'surprise':   {'emoji': '🎁', 'price': 2500, 'name': 'Sᴜʀᴘʀɪꜱᴇ Bᴏx'},
    'puppy':      {'emoji': '🐶', 'price': 3000, 'name': 'Pᴜᴘᴘʏ'},
    'cake':       {'emoji': '🎂', 'price': 1000, 'name': 'Cᴀᴋᴇ'},
    'loveletter': {'emoji': '💌', 'price': 400,  'name': 'Lᴏᴠᴇ Lᴇᴛᴛᴇʀ'},
    'cat':        {'emoji': '🐱', 'price': 2500, 'name': 'Cᴀᴛ'},
    'tulip':      {'emoji': '🌷', 'price': 1500, 'name': 'Tᴜʟɪᴘ'},
    'girlfriend': {'emoji': '👩‍❤️‍👨', 'price': 1000, 'name': 'Gɪʀʟ Fʀɪᴇɴᴅ'},
    'boyfriend':  {'emoji': '👨‍❤️‍👨', 'price': 1000, 'name': 'Bᴏʏ Fʀɪᴇɴᴅ'},
}

WORDS = [
    'pikachu', 'telegram', 'python', 'gaming', 'winner', 'dragon',
    'thunder', 'rainbow', 'galaxy', 'warrior', 'champion', 'diamond',
    'crystal', 'shadow', 'ninja', 'rocket', 'legend', 'phoenix',
    'cobra', 'tiger', 'panther', 'falcon', 'storm', 'blaze', 'spark',
    'viper', 'alpha', 'omega', 'zenith', 'cosmic', 'nebula', 'aurora',
    'eclipse', 'turbo', 'hyper', 'ultra', 'mega', 'super', 'rapid',
    'swift', 'flash', 'bolt', 'surge', 'prism', 'cipher', 'vertex',
]

CHATBOT_RESPONSES = [
    "haha lol 😂",
    "bro same 💀",
    "no way 😭",
    "that's actually fire 🔥",
    "okay but why 😭😭",
    "bro i was literally thinking the same 😭",
    "lmaooo 💀",
    "nah that's crazy 😂",
    "facts fr fr 💯",
    "bro stop 😭",
    "okay that's valid 🫡",
    "LMAO 💀💀",
    "wait what 😭",
    "bro i can't 😭😭",
    "that's honestly so true 💀",
    "ngl that's kinda funny 😂",
    "okay okay okay 👀",
    "i- 😶",
    "bruh 💀",
    "oof 😬",
    "slay 💅",
    "sheesh 😮",
    "based 🫡",
    "no literally 😭",
    "that's so real 💯",
    "haha nice 😄",
    "bro chill 😅",
    "ok and? 😂",
    "wait fr? 😮",
    "omg 😲",
    "bro...... 💀",
    "i mean fair enough 🤷",
    "you're not wrong 👀",
    "wild 😂",
    "respectfully.... no 😭",
    "hahaha okay 😂",
    "bro really said that 💀",
    "say less 👌",
    "yeah yeah yeah 😄",
    "nah bro ☠️",
    "on god 💯",
    "that's a W 🏆",
    "L take bro 💀",
    "i agree tbh 🤝",
    "aight bet 👍",
    "bro is wilding 😂",
    "this is sending me 😭",
    "real ones know 💯",
    "not you being right 😭",
    "okay i fw that 👀",
]

STICKER_COLLECTION_FILE = 'telegram-bot/sticker_collection.json'


def load_sticker_collection():
    try:
        with open(STICKER_COLLECTION_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []


def save_sticker_collection(collection):
    try:
        with open(STICKER_COLLECTION_FILE, 'w') as f:
            json.dump(collection, f)
    except Exception:
        pass


sticker_collection = load_sticker_collection()

card_games = {}
word_games = {}
bomb_games = {}


# ─── HELPERS ─────────────────────────────────────────────────────────────────

XP_RANKS = [
    (0,      1000,   "⚡ Rᴏᴏᴋɪᴇ"),
    (1000,   4000,   "🐢 Bᴇɢɪɴɴᴇʀ"),
    (4000,   20000,  "🔥 Aᴅᴠᴀɴᴄᴇᴅ"),
    (20000,  60000,  "💻 Hᴀᴄᴋᴇʀ"),
    (60000,  150000, "🧠 Uʟᴛʀᴀ Pʀᴏ Mᴀx Hᴀᴄᴋᴇʀ"),
    (150000, 5000000,"👑 Gᴏᴅ"),
]


def get_xp_rank(xp):
    for low, high, title in XP_RANKS:
        if xp < high:
            return title
    return "👑 Gᴏᴅ"


def get_xp_bar(xp):
    for low, high, title in XP_RANKS:
        if xp < high:
            current = xp - low
            total = high - low
            return f"({current:,}/{total:,}) {xp:,} xᴘ"
    return f"(MAX) {xp:,} xᴘ"


def _parse_tgem(em):
    """Returns (is_custom, emoji_id, fallback_char)"""
    if em and em.startswith('TGEM:'):
        parts = em.split(':', 2)
        emoji_id = parts[1] if len(parts) > 1 else ''
        fallback = parts[2] if len(parts) > 2 else '⭐'
        return True, emoji_id, fallback
    return False, None, em


def prefix(user, html=False):
    if user.get('is_premium'):
        em = user.get('premium_emoji') or '💓'
        is_custom, emoji_id, fallback = _parse_tgem(em)
        if is_custom:
            if html:
                return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
            return fallback
        return em
    return '👤'


def escape_html(text):
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def is_owner(update: Update) -> bool:
    username = (update.effective_user.username or '').lower()
    return username in OWNERS


def fmt(n):
    return f"${n:,}"


def gen_code(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def get_daily_amount(user):
    return 5000 if user.get('is_premium') else 2000


def get_rob_limit(user):
    return 400 if user.get('is_premium') else 200


def get_kill_limit(user):
    return 400 if user.get('is_premium') else 200


def get_rob_max(user):
    return 100000 if user.get('is_premium') else 10000


def get_tax_rate(user):
    return 0.05 if user.get('is_premium') else 0.10


def register_user(update: Update):
    u = update.effective_user
    username = (u.username or '').lower()
    get_user(u.id, name=u.full_name, username=u.username or '')
    if username in OWNERS:
        update_user(u.id, is_premium=1)
    chat = update.effective_chat
    if chat and chat.type != ChatType.PRIVATE:
        save_chat(chat.id, chat.title or '', chat.type)


async def schedule_delete(context, chat_id, message_id, delay=300):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass


async def is_admin(context, chat_id, user_id):
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except Exception:
        return False


async def resolve_target(update: Update, context):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    if context.args:
        try:
            uid = int(context.args[0])
            m = await context.bot.get_chat_member(update.effective_chat.id, uid)
            return m.user
        except Exception:
            pass
    return None


# ─── BASIC COMMANDS ───────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)

    u = update.effective_user
    user = get_user(u.id)
    p = prefix(user)

    text = (
        "✨ *Hey I'm Pikachu and these are my features below* 👇"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "👥 Groups",
                url="https://t.me/midnight_chatclub"
            ),
            InlineKeyboardButton(
                "👑 Owner",
                url="https://t.me/light_speedy"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 Channel",
                url="https://t.me/anonymous_rides"
            ),
            InlineKeyboardButton(
                "❓ Help",
                callback_data="help_menu"
            )
        ],
        [
            InlineKeyboardButton(
                "➕ Add Me To Your Group",
                url=f"https://t.me/{context.bot.username}?startgroup=true"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

    
    async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "help_menu":
        await help_command(update, context)
        

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    text = (
        "⚡ *Pɪᴋᴀᴄʜᴜ Bᴏᴛ — Cᴏᴍᴍᴀɴᴅꜱ* 🎮\n\n"
        "💰 *Eᴄᴏɴᴏᴍʏ:*\n"
        "`/bal` — Balance check\n"
        "`/daily` — Daily reward\n"
        "`/rob` — Rob someone (reply)\n"
        "`/kill` — Kill someone (reply)\n"
        "`/revive` — Revive (reply/self)\n"
        "`/protect 1d/2d` — Buy protection\n"
        "`/give <amount>` — Gift money (reply)\n"
        "`/toprich` — Top 10 richest\n"
        "`/topkill` — Top 10 killers\n\n"
        "🎁 *Iᴛᴇᴍꜱ:*\n"
        "`/items` — All items list\n"
        "`/item` — Check user items (reply)\n"
        "`/gift <name>` — Gift item (reply)\n\n"
        "🎮 *Gᴀᴍᴇꜱ:*\n"
        "`/card` — Start card game\n"
        "`/bet <amount>` — Join card game\n"
        "`/flip a/b/c/d` — Flip card\n"
        "`/wordgame <amount>` — Word typing game\n"
        "`/enter <amount>` — Join word game\n"
        "`/bomb <amount>` — Bomb game\n"
        "`/join <amount>` — Join bomb game\n"
        "`/pass` — Pass the bomb\n"
        "`/myrank` — Bomb rank\n"
        "`/leaders` — Bomb leaderboard\n\n"
        "👑 *Pʀᴇᴍɪᴜᴍ:*\n"
        "`/pay` — Get premium info\n"
        "`/check` — Check user protection\n"
        "`/setemoji <emoji>` — Custom emoji\n\n"
        "🛡️ *Gʀᴏᴜᴘ Mᴀɴᴀɢᴇᴍᴇɴᴛ:*\n"
        "`/promote 0/1/2/3` `/demote` `/title`\n"
        "`/ban` `/dban` `/dmute` `/unban` `/unmute`\n"
        "`/warn` `/unwarn` `/pin` `/unpin`\n\n"
        "🎫 *Cᴏᴅᴇꜱ:*\n"
        "`/redeem <code>` — Redeem balance code\n"
        "`/redxp <code>` — Redeem XP code\n"
        "`/claim` — Claim group reward"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


# ─── ECONOMY ─────────────────────────────────────────────────────────────────

async def bal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        user = get_user(target.id, name=target.full_name, username=target.username or '')
    else:
        u = update.effective_user
        user = get_user(u.id)

    rank = get_global_rank(user['user_id'])
    status = "☠️ Dᴇᴀᴅ" if user['is_dead'] else "✅ Aʟɪᴠᴇ"
    xp_rank = get_xp_rank(user['xp'])
    xp_bar = get_xp_bar(user['xp'])
    p = prefix(user, html=True)

    text = (
        f"{p} <b>Nᴀᴍᴇ:</b> {escape_html(user['name'])}\n"
        f"💰 <b>Bᴀʟᴀɴᴄᴇ:</b> {fmt(user['balance'])}\n"
        f"🏆 <b>Gʟᴏʙᴀʟ Rᴀɴᴋ:</b> #{rank}\n"
        f"❤️ <b>Sᴛᴀᴛᴜꜱ:</b> {status}\n"
        f"⚔️ <b>Kɪʟʟꜱ:</b> {user['kills']}\n"
        f"{xp_rank}: {xp_bar}"
    )
    msg = await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(context, update.effective_chat.id, msg.message_id))
    asyncio.create_task(schedule_delete(context, update.effective_chat.id, update.message.message_id))


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    user = get_user(u.id)
    now = int(time.time())
    last = user.get('daily_last', 0)

    if now - last < 86400:
        remaining = 86400 - (now - last)
        h = remaining // 3600
        m = (remaining % 3600) // 60
        await update.message.reply_text(
            f"⏰ *Not yet!*\n⏳ Come back in *{h}h {m}m*! 😅",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    amount = get_daily_amount(user)
    xp_gain = 100 if user.get('is_premium') else 50
    new_bal = user['balance'] + amount
    new_xp = user['xp'] + xp_gain
    update_user(u.id, balance=new_bal, xp=new_xp, daily_last=now)

    p = prefix(user)
    await update.message.reply_text(
        f"🎁 {p} *{u.first_name}* claimed their Daily Reward!\n\n"
        f"💰 *+{fmt(amount)}* received!\n"
        f"⚡ *+{xp_gain} XP* gained!\n"
        f"💵 *New Balance:* {fmt(new_bal)}",
        parse_mode=ParseMode.MARKDOWN
    )

async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to the person you want to rob! 😤")
        return

    # Amount check
    if not context.args:
        await update.message.reply_text("❌ Usage: /rob <amount>")
        return

    if not context.args[0].isdigit():
        await update.message.reply_text("❌ Please enter a valid amount!")
        return

    rob_amount = int(context.args[0])

    if rob_amount <= 0:
        await update.message.reply_text("❌ Amount must be greater than 0!")
        return

    target = update.message.reply_to_message.from_user

    if target.id == u.id or target.is_bot:
        await update.message.reply_text("❌ You can't rob yourself or a bot! 😂")
        return

    robber = get_user(u.id)
    victim = get_user(target.id, name=target.full_name, username=target.username or '')

    if robber.get('is_dead'):
        await update.message.reply_text("❌ You are dead! Use /revive first! 💀")
        return

    now = int(time.time())
    rob_count = robber.get('rob_count', 0)
    rob_reset = robber.get('rob_reset', 0)

    if now - rob_reset >= 86400:
        rob_count = 0
        rob_reset = now

    limit = get_rob_limit(robber)

    if rob_count >= limit:
        await update.message.reply_text(
            f"❌ Today's rob limit ({limit}) reached! Come back tomorrow! 😤"
        )
        return

    if victim.get('protection_until', 0) > now:
        prot_left = victim['protection_until'] - now
        h = prot_left // 3600
        m = (prot_left % 3600) // 60

        await update.message.reply_text(
            f"🛡️ *{target.first_name}* is protected!\n⏰ Try again in {h}h {m}m",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if victim['balance'] <= 0:
        await update.message.reply_text(
            f"❌ *{target.first_name}* has nothing to steal! 💸",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Max rob limit check
    max_rob = min(get_rob_max(robber), victim['balance'])

    if rob_amount > max_rob:
        await update.message.reply_text(
            f"❌ You can rob maximum {fmt(max_rob)} only!"
        )
        return

    tax = int(rob_amount * get_tax_rate(robber))
    net = rob_amount - tax
    xp_gain = random.randint(0, 100)

    update_user(
        u.id,
        balance=robber['balance'] + net,
        xp=robber['xp'] + xp_gain,
        rob_count=rob_count + 1,
        rob_reset=rob_reset
    )

    update_user(
        target.id,
        balance=max(0, victim['balance'] - rob_amount)
    )

    p_r = prefix(robber)
    p_v = prefix(victim)

    msg = await update.message.reply_text(
        f"🔫 *Rᴏʙ!*\n\n"
        f"{p_r} *{u.first_name}* ɴᴇ {p_v} *{target.first_name}* ꜱᴇ *{fmt(rob_amount)}* loot liya!\n"
        f"💸 Tax: {fmt(tax)} | 💰 Net: {fmt(net)}\n"
        f"⚡ +{xp_gain} XP",
        parse_mode=ParseMode.MARKDOWN
    )

    asyncio.create_task(
        schedule_delete(context, update.effective_chat.id, msg.message_id)
    )

    asyncio.create_task(
        schedule_delete(context, update.effective_chat.id, update.message.message_id)
    )


async def kill_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to the person you want to kill!")
        return

    target = update.message.reply_to_message.from_user
    if target.id == u.id or target.is_bot:
        await update.message.reply_text("❌ You can't kill yourself or a bot!")
        return

    killer = get_user(u.id)
    victim = get_user(target.id, name=target.full_name, username=target.username or '')

    if killer.get('is_dead'):
        await update.message.reply_text("❌ You are dead! Use /revive first! 💀")
        return
    if victim.get('is_dead'):
        await update.message.reply_text(
            f"❌ *{target.first_name}* is already dead! 💀",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    now = int(time.time())
    if victim.get('protection_until', 0) > now:
        await update.message.reply_text(
            f"🛡️ *{target.first_name}* is protected! Cannot be killed!",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    kill_count = killer.get('kill_count', 0)
    kill_reset = killer.get('kill_reset', 0)
    if now - kill_reset >= 86400:
        kill_count = 0
        kill_reset = now

    limit = get_kill_limit(killer)
    if kill_count >= limit:
        await update.message.reply_text(f"❌ Today's kill limit ({limit}) reached! Come back tomorrow!")
        return

    reward = random.randint(200, 400) if killer.get('is_premium') else random.randint(100, 200)
    xp_gain = random.randint(5, 10) if killer.get('is_premium') else random.randint(0, 5)

    update_user(u.id, balance=killer['balance'] + reward, kills=killer['kills'] + 1,
                xp=killer['xp'] + xp_gain, kill_count=kill_count + 1, kill_reset=kill_reset)
    update_user(target.id, is_dead=1)

    p_k = prefix(killer)
    p_v = prefix(victim)
    msg = await update.message.reply_text(
        f"⚔️ *Kɪʟʟ!*\n\n"
        f"{p_k} *{u.first_name}* killed {p_v} *{target.first_name}*! 💀\n"
        f"💰 Reward: {fmt(reward)}\n"
        f"⚡ +{xp_gain} XP",
        parse_mode=ParseMode.MARKDOWN
    )
    asyncio.create_task(schedule_delete(context, update.effective_chat.id, msg.message_id))
    asyncio.create_task(schedule_delete(context, update.effective_chat.id, update.message.message_id))


async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        victim = get_user(target.id, name=target.full_name, username=target.username or '')
        if not victim.get('is_dead'):
            await update.message.reply_text(
                f"❌ *{target.first_name}* is not dead!",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        update_user(target.id, is_dead=0)
        p = prefix(victim)
        await update.message.reply_text(
            f"💖 {p} *{target.first_name}* has been revived! ✨",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        user = get_user(u.id)
        if not user.get('is_dead'):
            await update.message.reply_text("❌ You are not dead! 😅")
            return
        update_user(u.id, is_dead=0)
        await update.message.reply_text(
            f"💖 *{u.first_name}* has been revived! ✨",
            parse_mode=ParseMode.MARKDOWN
        )


async def protect_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    user = get_user(u.id)

    # Agar argument nahi diya
    if not context.args:
        await update.message.reply_text(
            "❌ Use: /protect 1d or /protect 2d\n\n"
            "💰 1d = $400\n"
            "💓 2d = $1000 (Premium Only)",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    days_str = context.args[0].lower()

    # Sirf 1d aur 2d allow
    if days_str == '1d':
        days, cost = 1, 400

    elif days_str == '2d':
        # 2d sirf premium users ke liye
        if not user.get('is_premium'):
            await update.message.reply_text(
                "❌ 2d protection is only for 💓 Premium users! Use /pay"
            )
            return

        days, cost = 2, 1000

    else:
        await update.message.reply_text(
            "❌ Use only: /protect 1d or /protect 2d",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    now = int(time.time())

    # Agar pehle se protection active hai
    protection_until = user.get('protection_until', 0)

    if protection_until > now:
        remaining = protection_until - now
        remaining_days = round(remaining / 86400, 1)

        await update.message.reply_text(
            f"❌ Your protection is already active!\n\n"
            f"⏰ Remaining: *{remaining_days} day(s)*\n"
            f"⚠️ New protection tabhi le sakte ho jab current protection khatam ho jaye.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Balance check
    if user['balance'] < cost:
        await update.message.reply_text(
            f"❌ Insufficient balance!\n"
            f"💰 Need: {fmt(cost)} | Have: {fmt(user['balance'])}"
        )
        return

    # New protection activate
    new_prot = now + (days * 86400)

    update_user(
        u.id,
        balance=user['balance'] - cost,
        protection_until=new_prot
    )

    p = prefix(user)

    await update.message.reply_text(
        f"🛡️ {p} *{u.first_name}* ne *{days}d* protection liya!\n\n"
        f"💰 Cost: {fmt(cost)}\n"
        f"⏰ Protection active for *{days} day(s)*!",
        parse_mode=ParseMode.MARKDOWN
    )
    

async def give_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to the person you want to send money to!")
        return

    target = update.message.reply_to_message.from_user
    if target.id == u.id or target.is_bot:
        await update.message.reply_text("❌ You can't send to yourself or a bot!")
        return

    if not context.args:
        await update.message.reply_text("❌ Enter an amount! `/give <amount>`", parse_mode=ParseMode.MARKDOWN)
        return

    try:
        amount = int(context.args[0])
    except Exception:
        await update.message.reply_text("❌ Enter a valid amount!")
        return

    if amount <= 0:
        await update.message.reply_text("❌ Amount must be greater than 0!")
        return

    giver = get_user(u.id)
    receiver = get_user(target.id, name=target.full_name, username=target.username or '')

    tax_rate = get_tax_rate(giver)
    tax = int(amount * tax_rate)
    net = amount - tax  # receiver gets this

    if giver['balance'] < amount:
        await update.message.reply_text(
            f"❌ Insufficient balance!\n"
            f"💰 Need: {fmt(amount)}\n"
            f"💵 Have: {fmt(giver['balance'])}"
        )
        return

    update_user(u.id, balance=giver['balance'] - amount)
    update_user(target.id, balance=receiver['balance'] + net)

    p_g = prefix(giver)
    p_r = prefix(receiver)
    msg = await update.message.reply_text(
        f"💸 *Gɪᴠᴇ!*\n\n"
        f"{p_g} *{u.first_name}* sent {p_r} *{target.first_name}*: *{fmt(amount)}*\n"
        f"💸 Tax ({int(tax_rate*100)}%): -{fmt(tax)}\n"
        f"✅ *{target.first_name}* received: *{fmt(net)}*",
        parse_mode=ParseMode.MARKDOWN
    )
    asyncio.create_task(schedule_delete(context, update.effective_chat.id, msg.message_id))
    asyncio.create_task(schedule_delete(context, update.effective_chat.id, update.message.message_id))


async def toprich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    users = get_top_rich(10)
    text = "💰 <b>Tᴏᴘ 10 Rɪᴄʜᴇꜱᴛ Uꜱᴇʀꜱ</b> 🏆\n\n"
    medals = ['🥇', '🥈', '🥉'] + ['🔸'] * 7
    for i, user in enumerate(users):
        p = prefix(user, html=True)
        text += f"{medals[i]} {p} <b>{escape_html(user['name'])}</b> — {fmt(user['balance'])}\n"
    msg = await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(context, update.effective_chat.id, msg.message_id))


async def topkill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    users = get_top_kills(10)
    text = "⚔️ <b>Tᴏᴘ 10 Kɪʟʟᴇʀꜱ</b> 💀\n\n"
    medals = ['🥇', '🥈', '🥉'] + ['🔸'] * 7
    for i, user in enumerate(users):
        p = prefix(user, html=True)
        text += f"{medals[i]} {p} <b>{escape_html(user['name'])}</b> — {user['kills']} kills\n"
    msg = await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(context, update.effective_chat.id, msg.message_id))


async def pay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)

    # Agar group/chat mein command use hui
    if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        keyboard = [
            [
                InlineKeyboardButton(
                    "💌 Open Bot DM",
                    url="https://t.me/Pikachu_ibot"
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "💎 *Premium Purchase*\n\n"
            "To buy premium, please open the bot in DM first.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        return

    # Agar DM mein /pay use kare
    keyboard = [
        [
            InlineKeyboardButton(
                "👑 Owner",
                url="https://t.me/light_speedy"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "╔══❖•ೋ° °ೋ•❖══╗\n"
        "      👑 *PREMIUM ACCESS* 👑\n"
        "╚══❖•ೋ° °ೋ•❖══╝\n\n"

        "✨ Upgrade your experience with premium benefits.\n\n"

        "💸 *Premium Price:* ₹20 Only\n\n"

        "📩 To purchase premium,\n"
        "contact the owner directly.\n\n"

        "⚡ Fast Response\n"
        "🔒 Trusted Payment\n"
        "🎖 Instant Premium Access\n\n"

        "👇 Click the button below to contact owner.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )


# ─── ITEMS ────────────────────────────────────────────────────────────────────

async def items_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    text = "🎁 *Aᴠᴀɪʟᴀʙʟᴇ Gɪꜰᴛ Iᴛᴇᴍꜱ* ⚡\n\n"
    for key, item in GIFT_ITEMS.items():
        text += f"{item['emoji']} *{item['name']}* — {fmt(item['price'])}\n"
    text += f"\n📦 `/gift <name>` (reply) — Send a gift!\nExample: `/gift rose`"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def item_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        user = get_user(target.id, name=target.full_name, username=target.username or '')
        name = target.first_name
    else:
        u = update.effective_user
        user = get_user(u.id)
        name = u.first_name

    items = json.loads(user.get('items') or '{}')
    if not items or all(v == 0 for v in items.values()):
        await update.message.reply_text(
            f"📭 *{name}* has no items! 😅",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    text = f"🎁 *{name}* ᴋᴇ Items:\n\n"
    for key, count in items.items():
        item = GIFT_ITEMS.get(key, {})
        if item and count > 0:
            text += f"{item['emoji']} {item['name']}: {count}x\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def gift_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to the person you want to gift!")
        return
    if not context.args:
        await update.message.reply_text(
            "❌ Enter an item name!\n`/gift <name>`\n\nItems: rose, chocolate, ring, teddy, pizza, surprise, puppy, cake, loveletter, cat, tulip, girlfriend, boyfriend",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    item_name = context.args[0].lower()
    if item_name not in GIFT_ITEMS:
        await update.message.reply_text("❌ Invalid item! Check `/items`", parse_mode=ParseMode.MARKDOWN)
        return

    target = update.message.reply_to_message.from_user
    if target.id == u.id or target.is_bot:
        await update.message.reply_text("❌ You can't gift to yourself or a bot!")
        return

    item = GIFT_ITEMS[item_name]
    giver = get_user(u.id)
    receiver = get_user(target.id, name=target.full_name, username=target.username or '')

    if giver['balance'] < item['price']:
        await update.message.reply_text(
            f"❌ Insufficient balance!\n💰 Need: {fmt(item['price'])} | Have: {fmt(giver['balance'])}"
        )
        return

    update_user(u.id, balance=giver['balance'] - item['price'])
    recv_items = json.loads(receiver.get('items') or '{}')
    recv_items[item_name] = recv_items.get(item_name, 0) + 1
    update_user(target.id, items=json.dumps(recv_items))

    await update.message.reply_text(
        f"{item['emoji']} *Gift!*\n\n"
        f"*{u.first_name}* ɴᴇ *{target.first_name}* ko *{item['name']}* gift kiya! 🎉\n"
        f"💰 Cost: {fmt(item['price'])}",
        parse_mode=ParseMode.MARKDOWN
    )


# ─── PREMIUM ─────────────────────────────────────────────────────────────────

async def set_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    user = get_user(u.id)
    if not user.get('is_premium'):
        await update.message.reply_text("❌ This command is for 💓 Premium users only! /pay")
        return

    msg_text = update.message.text or ''
    entities = update.message.entities or []

    # Detect Telegram Premium custom emoji entity (after the /setemoji command)
    custom_emoji_id = None
    fallback_char = None
    for entity in entities:
        if getattr(entity, 'type', None) == 'custom_emoji':
            start = entity.offset
            length = entity.length
            # Extract the fallback character from the raw text
            try:
                char = msg_text[start: start + length]
            except Exception:
                char = '⭐'
            custom_emoji_id = getattr(entity, 'custom_emoji_id', None)
            fallback_char = char
            break

    if custom_emoji_id:
        emoji_val = f"TGEM:{custom_emoji_id}:{fallback_char}"
        update_user(u.id, premium_emoji=emoji_val)
        preview = f'<tg-emoji emoji-id="{custom_emoji_id}">{escape_html(fallback_char)}</tg-emoji>'
        await update.message.reply_text(
            f"✅ Your prefix is now this Telegram Premium emoji! {preview}\n"
            f"<i>Others will see your animated emoji in /bal! ✨</i>",
            parse_mode=ParseMode.HTML
        )
        return


async def check_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)

    u = update.effective_user
    user = get_user(u.id)

    # Premium check
    if not user.get('is_premium'):
        await update.message.reply_text(
            "❌ This command is for 💓 Premium users only!\nUse /pay",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Target user find
    target = None

    # Reply method
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user

    # Username/ID method
    elif context.args:
        arg = context.args[0]

        # Username
        if arg.startswith("@"):
            target_name = arg.replace("@", "")
            target = type("obj", (object,), {
                "id": 0,
                "first_name": target_name,
                "full_name": target_name,
                "username": target_name
            })

        # ID
        elif arg.isdigit():
            target = type("obj", (object,), {
                "id": int(arg),
                "first_name": f"User {arg}",
                "full_name": f"User {arg}",
                "username": ""
            })

    # Agar target nahi mila
    if not target:
        await update.message.reply_text(
            "❌ Reply to a user or use:\n"
            "`/check @username`\n"
            "`/check user_id`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Group mein use hua
    if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:

        # Victim data
        victim = get_user(
            target.id,
            name=target.full_name,
            username=target.username or ''
        )

        now = int(time.time())
        prot = victim.get('protection_until', 0)

        if prot > now:
            remaining = prot - now
            h = remaining // 3600
            m = (remaining % 3600) // 60

            dm_text = (
                f"🛡️ *Protection Status*\n\n"
                f"👤 User: *{target.first_name}*\n"
                f"✅ Protection Active\n"
                f"⏰ Remaining: {h}h {m}m"
            )
        else:
            dm_text = (
                f"🛡️ *Protection Status*\n\n"
                f"👤 User: *{target.first_name}*\n"
                f"❌ No Active Protection"
            )

        # DM bhejne ki koshish
        try:
            await context.bot.send_message(
                chat_id=u.id,
                text=dm_text,
                parse_mode=ParseMode.MARKDOWN
            )

            keyboard = [
                [
                    InlineKeyboardButton(
                        "🔍 Open DM & Check",
                        url="https://t.me/Pikachu_ibot"
                    )
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "✅ Protection details sent to your DM.",
                reply_markup=reply_markup
            )

        except:
            keyboard = [
                [
                    InlineKeyboardButton(
                        "💌 Open Bot DM",
                        url="https://t.me/Pikachu_ibot"
                    )
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "❌ First start the bot in DM to use this command.",
                reply_markup=reply_markup
            )

        return

    # DM mein direct command use hui
    victim = get_user(
        target.id,
        name=target.full_name,
        username=target.username or ''
    )

    now = int(time.time())
    prot = victim.get('protection_until', 0)

    if prot > now:
        remaining = prot - now
        h = remaining // 3600
        m = (remaining % 3600) // 60

        text = (
            f"🛡️ *Protection Status*\n\n"
            f"👤 User: *{target.first_name}*\n"
            f"✅ Protection Active\n"
            f"⏰ Remaining: {h}h {m}m"
        )
    else:
        text = (
            f"🛡️ *Protection Status*\n\n"
            f"👤 User: *{target.first_name}*\n"
            f"❌ No Active Protection"
        )

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN
    )
    

# ─── CLAIM ────────────────────────────────────────────────────────────────────

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat = update.effective_chat

    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text("❌ Use this command in a group!")
        return

    try:
        count = await context.bot.get_chat_member_count(chat.id)
    except Exception:
        count = 0

    if count < 500:
        await update.message.reply_text(
            f"❌ Group needs 500+ members!\n"
            f"👥 Currently: *{count}* members",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    group = get_group(chat.id)
    if group and group.get('claimed_by'):
        await update.message.reply_text("❌ This group's reward has already been claimed!")
        return

    reward = min(count * 10, 100000)
    save_group(chat.id, u.id)
    user = get_user(u.id)
    update_user(u.id, balance=user['balance'] + reward)

    await update.message.reply_text(
        f"🎉 *Claim Successful!*\n\n"
        f"👥 Group members: {count}\n"
        f"💰 Reward: *{fmt(reward)}* received!\n"
        f"💵 New Balance: {fmt(user['balance'] + reward)}",
        parse_mode=ParseMode.MARKDOWN
    )


# ─── OWNER COMMANDS ───────────────────────────────────────────────────────────

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    if not is_owner(update):
        await update.message.reply_text("❌ Only bot owners can do this!")
        return
    if not context.args:
        await update.message.reply_text("❌ Enter a message! `/broadcast <message>`", parse_mode=ParseMode.MARKDOWN)
        return

    msg_text = ' '.join(context.args)
    all_users = get_all_users()
    success = 0
    fail = 0

    status_msg = await update.message.reply_text(f"📢 Broadcasting to {len(all_users)} users...")

    for user in all_users:
        try:
            await context.bot.send_message(
                chat_id=user['user_id'],
                text=f"📢 *Broadcast Message:*\n\n{msg_text}",
                parse_mode=ParseMode.MARKDOWN
            )
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            fail += 1

    await status_msg.edit_text(
        f"✅ Broadcast done!\n✅ Success: {success}\n❌ Failed: {fail}"
    )


async def cancel_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    if not is_owner(update):
        await update.message.reply_text("❌ Only bot owners can do this!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a user's message!")
        return
    target = update.message.reply_to_message.from_user
    update_user(target.id, is_premium=0, premium_emoji='')
    await update.message.reply_text(
        f"❌ *{target.first_name}*'s Premium has been cancelled!",
        parse_mode=ParseMode.MARKDOWN
    )


async def give_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    if not is_owner(update):
        await update.message.reply_text("❌ Only bot owners can do this!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a user's message!")
        return
    target = update.message.reply_to_message.from_user
    get_user(target.id, name=target.full_name, username=target.username or '')
    update_user(target.id, is_premium=1)
    await update.message.reply_text(
        f"💓 *{target.first_name}* has been given Premium! 🎉",
        parse_mode=ParseMode.MARKDOWN
    )


async def setbal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    if not is_owner(update):
        await update.message.reply_text("❌ Only bot owners can do this!")
        return
    if not context.args:
        await update.message.reply_text("❌ `/setbal <amount>` (reply to user)", parse_mode=ParseMode.MARKDOWN)
        return

    try:
        amount = int(context.args[0])
    except Exception:
        await update.message.reply_text("❌ Enter a valid amount!")
        return

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        get_user(target.id, name=target.full_name, username=target.username or '')
        update_user(target.id, balance=amount)
        await update.message.reply_text(
            f"✅ *{target.first_name}*'s balance set to: {fmt(amount)}",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        u = update.effective_user
        update_user(u.id, balance=amount)
        await update.message.reply_text(f"✅ Your balance has been set to: {fmt(amount)}")


async def gen_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    if not is_owner(update):
        await update.message.reply_text("❌ Only bot owners can do this!")
        return
    if not context.args:
        await update.message.reply_text("❌ `/gen <amount>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        amount = int(context.args[0])
    except Exception:
        await update.message.reply_text("❌ Enter a valid amount!")
        return

    code = gen_code()
    save_code(code, amount, 'balance')
    await update.message.reply_text(
        f"✅ *Balance Code Generated!*\n\n"
        f"🎫 *Code:* `{code}`\n"
        f"💰 *Amount:* {fmt(amount)}\n\n"
        f"Redeem: `/redeem {code}`",
        parse_mode=ParseMode.MARKDOWN
    )


async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    if not context.args:
        await update.message.reply_text("❌ `/redeem <code>`", parse_mode=ParseMode.MARKDOWN)
        return

    code = context.args[0].upper()
    result, error = use_code(code, u.id)
    if error:
        await update.message.reply_text(error)
        return
    if result['type'] != 'balance':
        await update.message.reply_text("❌ This is not a balance code! Use `/redxp` for XP codes", parse_mode=ParseMode.MARKDOWN)
        return

    user = get_user(u.id)
    update_user(u.id, balance=user['balance'] + result['amount'])
    await update.message.reply_text(
        f"🎉 *Code Redeemed!*\n\n"
        f"💰 *+{fmt(result['amount'])}* received!\n"
        f"💵 New Balance: {fmt(user['balance'] + result['amount'])}",
        parse_mode=ParseMode.MARKDOWN
    )


async def xp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    if not is_owner(update):
        await update.message.reply_text("❌ Only bot owners can do this!")
        return
    if not context.args:
        await update.message.reply_text("❌ `/xp <amount>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        amount = int(context.args[0])
    except Exception:
        await update.message.reply_text("❌ Enter a valid amount!")
        return

    code = gen_code()
    save_code(code, amount, 'xp')
    await update.message.reply_text(
        f"✅ *XP Code Generated!*\n\n"
        f"🎫 *Code:* `{code}`\n"
        f"⚡ *XP:* {amount}\n\n"
        f"Redeem: `/redxp {code}`",
        parse_mode=ParseMode.MARKDOWN
    )


async def redxp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    if not context.args:
        await update.message.reply_text("❌ `/redxp <code>`", parse_mode=ParseMode.MARKDOWN)
        return

    code = context.args[0].upper()
    result, error = use_code(code, u.id)
    if error:
        await update.message.reply_text(error)
        return
    if result['type'] != 'xp':
        await update.message.reply_text("❌ This is not an XP code! Use `/redeem` for balance codes", parse_mode=ParseMode.MARKDOWN)
        return

    user = get_user(u.id)
    update_user(u.id, xp=user['xp'] + result['amount'])
    await update.message.reply_text(
        f"🎉 *XP Code Redeemed!*\n\n"
        f"⚡ *+{result['amount']} XP* received!\n"
        f"🏅 New XP: {user['xp'] + result['amount']}\n"
        f"🎖️ Rank: {get_xp_rank(user['xp'] + result['amount'])}",
        parse_mode=ParseMode.MARKDOWN
    )


# ─── GROUP MANAGEMENT ─────────────────────────────────────────────────────────

async def promote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat = update.effective_chat
    if not await is_admin(context, chat.id, u.id):
        await update.message.reply_text("❌ Only admins can do this!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a user's message!\nUsage: `/promote 0/1/2/3`", parse_mode=ParseMode.MARKDOWN)
        return

    target = update.message.reply_to_message.from_user
    level = 1
    if context.args:
        try:
            level = int(context.args[0])
        except Exception:
            pass

    try:
        if level == 0:
            await context.bot.promote_chat_member(chat.id, target.id,
                can_manage_chat=False, can_delete_messages=False,
                can_restrict_members=False, can_promote_members=False)
        elif level == 1:
            await context.bot.promote_chat_member(chat.id, target.id,
                can_manage_chat=True, can_delete_messages=True,
                can_restrict_members=False, can_promote_members=False)
        elif level == 2:
            await context.bot.promote_chat_member(chat.id, target.id,
                can_manage_chat=True, can_delete_messages=True,
                can_restrict_members=True, can_promote_members=False)
        elif level == 3:
            await context.bot.promote_chat_member(chat.id, target.id,
                can_manage_chat=True, can_delete_messages=True,
                can_restrict_members=True, can_promote_members=True)
        await update.message.reply_text(
            f"✅ *{target.first_name}* promoted! (Level {level})",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def demote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat = update.effective_chat
    if not await is_admin(context, chat.id, u.id):
        await update.message.reply_text("❌ Only admins can do this!")
        return
    target = await resolve_target(update, context)
    if not target:
        await update.message.reply_text("❌ Select a user via reply or ID!")
        return
    try:
        await context.bot.promote_chat_member(chat.id, target.id,
            can_manage_chat=False, can_delete_messages=False,
            can_restrict_members=False, can_promote_members=False)
        await update.message.reply_text(f"✅ *{target.first_name}* demoted!", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def title_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat = update.effective_chat
    if not await is_admin(context, chat.id, u.id):
        await update.message.reply_text("❌ Only admins can do this!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a user's message!")
        return
    if not context.args:
        await update.message.reply_text("❌ Enter a title! `/title <title name>`", parse_mode=ParseMode.MARKDOWN)
        return
    target = update.message.reply_to_message.from_user
    title = ' '.join(context.args)
    try:
        await context.bot.set_chat_administrator_custom_title(chat.id, target.id, title)
        await update.message.reply_text(
            f"✅ *{target.first_name}*'s title set to: *{title}*",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat = update.effective_chat
    if not await is_admin(context, chat.id, u.id):
        await update.message.reply_text("❌ Only admins can do this!")
        return
    target = await resolve_target(update, context)
    if not target:
        await update.message.reply_text("❌ Select a user via reply or ID!")
        return
    try:
        await context.bot.ban_chat_member(chat.id, target.id)
        await update.message.reply_text(
            f"🔨 *{target.first_name}* has been banned! 👋",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def dban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat = update.effective_chat
    if not await is_admin(context, chat.id, u.id):
        await update.message.reply_text("❌ Only admins can do this!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message first!")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.delete_message(chat.id, update.message.reply_to_message.message_id)
        await context.bot.ban_chat_member(chat.id, target.id)
        await update.message.reply_text(
            f"🔨 *{target.first_name}* has been banned and their message deleted! 👋",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def dmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat = update.effective_chat
    if not await is_admin(context, chat.id, u.id):
        await update.message.reply_text("❌ Only admins can do this!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message first!")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.delete_message(chat.id, update.message.reply_to_message.message_id)
        await context.bot.restrict_chat_member(
            chat.id, target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text(
            f"🔇 *{target.first_name}* has been muted and their message deleted!",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat = update.effective_chat
    if not await is_admin(context, chat.id, u.id):
        await update.message.reply_text("❌ Only admins can do this!")
        return
    target = await resolve_target(update, context)
    if not target:
        await update.message.reply_text("❌ Select a user via reply or ID!")
        return
    try:
        await context.bot.unban_chat_member(chat.id, target.id)
        await update.message.reply_text(
            f"✅ *{target.first_name}* has been unbanned!",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def unmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat = update.effective_chat
    if not await is_admin(context, chat.id, u.id):
        await update.message.reply_text("❌ Only admins can do this!")
        return
    target = await resolve_target(update, context)
    if not target:
        await update.message.reply_text("❌ Select a user via reply or ID!")
        return
    try:
        await context.bot.restrict_chat_member(
            chat.id, target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await update.message.reply_text(
            f"✅ *{target.first_name}* has been unmuted!",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def warn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat = update.effective_chat
    if not await is_admin(context, chat.id, u.id):
        await update.message.reply_text("❌ Only admins can do this!")
        return
    target = await resolve_target(update, context)
    if not target:
        await update.message.reply_text("❌ Select a user via reply or ID!")
        return
    count = add_warning(chat.id, target.id)
    text = (
        f"⚠️ *{target.first_name}* has been warned! (Warning #{count})\n"
        f"{'🔨 3 warnings = auto ban!' if count >= 3 else f'⚠️ {3-count} warnings remaining'}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    if count >= 3:
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            await update.message.reply_text(
                f"🔨 *{target.first_name}* has been banned after 3 warnings!",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            pass


async def unwarn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat = update.effective_chat
    if not await is_admin(context, chat.id, u.id):
        await update.message.reply_text("❌ Only admins can do this!")
        return
    target = await resolve_target(update, context)
    if not target:
        await update.message.reply_text("❌ Select a user via reply or ID!")
        return
    remove_warning(chat.id, target.id)
    count = get_warnings(chat.id, target.id)
    await update.message.reply_text(
        f"✅ *{target.first_name}* ki 1 warning remove hui! Remaining: {count}",
        parse_mode=ParseMode.MARKDOWN
    )


async def pin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat = update.effective_chat
    if not await is_admin(context, chat.id, u.id):
        await update.message.reply_text("❌ Only admins can do this!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message first!")
        return
    try:
        await context.bot.pin_chat_message(chat.id, update.message.reply_to_message.message_id)
        await update.message.reply_text("📌 Message has been pinned!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def unpin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat = update.effective_chat
    if not await is_admin(context, chat.id, u.id):
        await update.message.reply_text("❌ Only admins can do this!")
        return
    try:
        if update.message.reply_to_message:
            await context.bot.unpin_chat_message(chat.id, update.message.reply_to_message.message_id)
        else:
            await context.bot.unpin_all_chat_messages(chat.id)
        await update.message.reply_text("✅ Message has been unpinned!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


# ─── CARD GAME ────────────────────────────────────────────────────────────────


def make_cards_for_sum(total_sum):
    while True:
        a = random.randint(1, min(10, total_sum - 3))
        b = random.randint(1, min(10, total_sum - a - 2))
        c = random.randint(1, min(10, total_sum - a - b - 1))
        d = total_sum - a - b - c
        if 1 <= d <= 10:
            cards = [a, b, c, d]
            random.shuffle(cards)
            return cards


async def card_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)

    u = update.effective_user
    chat_id = update.effective_chat.id

    if update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text("❌ Card game can only be played in groups!")
        return

    if chat_id in card_games:
        await update.message.reply_text("❌ A card game is already running in this group!")
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Use:\n`/card <amount>`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    try:
        amount = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid amount!")
        return

    if amount <= 0:
        await update.message.reply_text("❌ Amount must be greater than 0!")
        return

    host = get_user(u.id)

    if host['balance'] < amount:
        await update.message.reply_text(
            f"❌ Insufficient balance!\nNeed: {fmt(amount)}"
        )
        return

    update_user(u.id, balance=host['balance'] - amount)

    card_games[chat_id] = {
        'creator': u.id,
        'players': {
            u.id: {
                'name': u.first_name,
                'bet': amount
            }
        },
        'round': 0,
        'started': False,
        'bet': amount,
        'pot': amount,
        'total_sum': random.randint(16, 28),
        'round_moves': {},
        'scores': {},
        'turn_order': [],
        'turn_index': 0
    }

    await update.message.reply_text(
        f"🃏 *CARD GAME CREATED*\n\n"
        f"👤 Host: {u.mention_markdown_v2()}\n"
        f"💰 Bet Amount: {fmt(amount)}\n\n"
        f"⚡ Join using:\n`/bet {amount}`\n\n"
        f"⏰ Join Time: 90 Seconds",
        parse_mode=ParseMode.MARKDOWN_V2
    )

    asyncio.create_task(card_join_timer(context, chat_id))


async def card_join_timer(context, chat_id):
    timings = [90, 60, 40, 20]

    for t in timings:

        game = card_games.get(chat_id)

        if not game or game['started']:
            return

        await context.bot.send_message(
            chat_id,
            f"⏰ *{t} seconds left!*\n"
            f"Use `/bet {game['bet']}` to join the card game!",
            parse_mode=ParseMode.MARKDOWN
        )

        if t == 90:
            await asyncio.sleep(30)
        elif t == 60:
            await asyncio.sleep(20)
        elif t == 40:
            await asyncio.sleep(20)
        elif t == 20:
            await asyncio.sleep(20)

    game = card_games.get(chat_id)

    if not game or game['started']:
        return

    if len(game['players']) < 2:
        del card_games[chat_id]

        await context.bot.send_message(
            chat_id,
            "❌ Card game cancelled!\nNeed at least 2 players."
        )
        return

    await begin_card_game(context, chat_id)


async def start_card_after_delay(context, chat_id):
    await asyncio.sleep(60)
    game = card_games.get(chat_id)
    if not game or game['started']:
        return
    if len(game['players']) < 2:
        if chat_id in card_games:
            del card_games[chat_id]
        await context.bot.send_message(chat_id, "❌ Card game cancelled! Need 2+ players.")
        return
    await begin_card_game(context, chat_id)


async def begin_card_game(context, chat_id):
    game = card_games[chat_id]

    game['started'] = True
    game['round'] = 1

    total = game['total_sum']

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🃏 Check Cards",
                url="https://t.me/Pikachu_ibot"
            )
        ]
    ])

    for uid in game['players']:

        cards = make_cards_for_sum(total)

        game['players'][uid]['cards'] = {
            'a': cards[0],
            'b': cards[1],
            'c': cards[2],
            'd': cards[3]
        }

        game['players'][uid]['used'] = []

        game['scores'][uid] = 0

        try:
            await context.bot.send_message(
                uid,
                f"🃏 *YOUR SECRET CARDS*\n\n"
                f"🅰️ A = {cards[0]}\n"
                f"🅱️ B = {cards[1]}\n"
                f"🅲 C = {cards[2]}\n"
                f"🅳 D = {cards[3]}\n\n"
                f"🎯 Total Sum = {total}\n\n"
                f"Use `/flip a/b/c/d` in group!",
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            pass

    player_list = "\n".join(
        f"• {x['name']}" for x in game['players'].values()
    )

    game['turn_order'] = list(game['players'].keys())
    first_uid = game['turn_order'][0]
    first_name = game['players'][first_uid]['name']

    await context.bot.send_message(
        chat_id,
        f"🎮 *CARD GAME STARTED!*\n\n"
        f"👥 Players:\n{player_list}\n\n"
        f"💰 Pot: {fmt(game['pot'])}\n\n"
        f"📩 Card details sent to your DM.\n\n"
        f"🎯 Round 1/4\n"
        f"👉 Turn: *{first_name}*\n"
        f"Use `/flip a/b/c/d`",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )

    asyncio.create_task(card_round_timer(context, chat_id))

    for uid in game['players']:

        cards = make_cards_for_sum(total)

        game['players'][uid]['cards'] = {
            'a': cards[0],
            'b': cards[1],
            'c': cards[2],
            'd': cards[3]
        }

        game['players'][uid]['used'] = []

        game['scores'][uid] = 0

        try:
            await context.bot.send_message(
                uid,
                f"🃏 *YOUR SECRET CARDS*\n\n"
                f"🅰️ A = {cards[0]}\n"
                f"🅱️ B = {cards[1]}\n"
                f"🅲 C = {cards[2]}\n"
                f"🅳 D = {cards[3]}\n\n"
                f"🎯 Total Sum = {total}\n\n"
                f"Use `/flip a/b/c/d` in group!",
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            pass

    player_list = "\n".join(
        f"• {x['name']}" for x in game['players'].values()
    )

    game['turn_order'] = list(game['players'].keys())
    first_uid = game['turn_order'][0]
    first_name = game['players'][first_uid]['name']

    await context.bot.send_message(
        chat_id,
        f"🎮 *CARD GAME STARTED!*\n\n"
        f"👥 Players:\n{player_list}\n\n"
        f"💰 Pot: {fmt(game['pot'])}\n\n"
        f"📩 Card details sent to your DM.\n\n"
        f"🎯 Round 1/4\n"
        f"👉 Turn: *{first_name}*\n"
        f"Use `/flip a/b/c/d`",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )

    asyncio.create_task(card_round_timer(context, chat_id))

async def card_round_timer(context, chat_id):
    await asyncio.sleep(60)
    game = card_games.get(chat_id)
    if not game or not game['started']:
        return
    await process_card_round(context, chat_id, auto=True)


async def bet_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat_id = update.effective_chat.id

    game = card_games.get(chat_id)
    if not game:
        await update.message.reply_text("❌ No card game is running! Use `/card` to start one", parse_mode=ParseMode.MARKDOWN)
        return
    if game['started']:
        await update.message.reply_text("❌ Game already started! Join next time 😅")
        return
    if u.id in game['players']:
        await update.message.reply_text("❌ You have already joined!")
        return
    if not context.args:
        await update.message.reply_text("❌ `/bet <amount>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        amount = int(context.args[0])
    except Exception:
        await update.message.reply_text("❌ Enter a valid amount!")
        return
    if amount <= 0:
        await update.message.reply_text("❌ Amount must be greater than 0!")
        return

    if game['bet'] == 0:
        game['bet'] = amount
    elif amount != game['bet']:
        await update.message.reply_text(f"❌ Bet must be {fmt(game['bet'])}!")
        return

    user = get_user(u.id)
    if user['balance'] < amount:
        await update.message.reply_text(f"❌ Insufficient balance! Have {fmt(user['balance'])}")
        return

    update_user(u.id, balance=user['balance'] - amount)
    game['players'][u.id] = {'name': u.first_name, 'bet': amount}
    game['pot'] += amount

    await update.message.reply_text(
        f"✅ *{u.first_name}* joined!\n"
        f"👥 Players: {len(game['players'])} | 💰 Pot: {fmt(game['pot'])}",
        parse_mode=ParseMode.MARKDOWN
    )
    asyncio.create_task(schedule_delete(context, chat_id, update.message.message_id))


async def flip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)

    u = update.effective_user
    chat_id = update.effective_chat.id

    game = card_games.get(chat_id)

    if not game or not game['started']:
        await update.message.reply_text("❌ No card game running!")
        return

    if u.id not in game['players']:
        await update.message.reply_text("❌ You are not in this game!")
        return

    current_turn_uid = game['turn_order'][game['turn_index']]

    if u.id != current_turn_uid:
        turn_name = game['players'][current_turn_uid]['name']

        await update.message.reply_text(
            f"⏳ Wait for your turn!\n"
            f"👉 Current turn: *{turn_name}*",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Use `/flip a/b/c/d`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    card_letter = context.args[0].lower()

    if card_letter not in ['a', 'b', 'c', 'd']:
        await update.message.reply_text("❌ Invalid card!")
        return

    player = game['players'][u.id]

    if card_letter in player['used']:
        await update.message.reply_text(
            "❌ Card already used!"
        )
        return

    value = player['cards'][card_letter]

    player['used'].append(card_letter)

    game['round_moves'][u.id] = card_letter

    await update.message.reply_text(
        f"🃏 *{u.first_name}* flipped "
        f"*{card_letter.upper()}* = *{value}*",
        parse_mode=ParseMode.MARKDOWN
    )

    game['turn_index'] += 1

    if game['turn_index'] >= len(game['turn_order']):

        game['turn_index'] = 0

        await process_card_round(context, chat_id)

        return

    next_uid = game['turn_order'][game['turn_index']]
    next_name = game['players'][next_uid]['name']

    await context.bot.send_message(
        chat_id,
        f"👉 Now turn of *{next_name}*\n"
        f"Use `/flip a/b/c/d`",
        parse_mode=ParseMode.MARKDOWN
    )


async def process_card_round(context, chat_id, auto=False):
    game = card_games.get(chat_id)
    if not game or not game['started']:
        return

    current_round = game['round']
    moves = game.get('round_moves', {})

    text = f"🃏 *Round {current_round}/4 Result:*\n\n"
    round_values = {}

    for uid, data in game['players'].items():
        cards = data.get('cards', {})
        used = data.get('used', [])
        if uid in moves:
            card_letter = moves[uid]
        else:
            remaining = [k for k in ['a', 'b', 'c', 'd'] if k not in used]
            card_letter = random.choice(remaining) if remaining else 'a'

        val = cards.get(card_letter, 0)
        round_values[uid] = (card_letter, val)
        data['used'].append(card_letter)
        text += f"• *{data['name']}*: Card {card_letter.upper()} = {val}\n"

    if round_values:
        max_val = max(v for _, v in round_values.values())
        winners_round = [uid for uid, (_, v) in round_values.items() if v == max_val]
        if len(winners_round) == 1:
            winner_uid = winners_round[0]
            game['scores'][winner_uid] = game['scores'].get(winner_uid, 0) + 1
            text += f"\n🏆 Round winner: *{game['players'][winner_uid]['name']}*!"
        else:
            text += f"\n🤝 Round tie!"

    game['round_moves'] = {}

    if current_round >= 4:
        await context.bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN)
        await end_card_game(context, chat_id)
    else:
        game['round'] = current_round + 1
        text += f"\n\n🔔 *Round {game['round']}/4* — Use `/flip a/b/c/d`!\n⏰ 60 seconds!"
        await context.bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN)
        asyncio.create_task(card_round_timer(context, chat_id))


async def end_card_game(context, chat_id):
    game = card_games.get(chat_id)
    if not game:
        return

    scores = game.get('scores', {})
    if not scores:
        del card_games[chat_id]
        return

    max_score = max(scores.values())
    winners = [uid for uid, s in scores.items() if s == max_score]
    winner_uid = random.choice(winners)
    winner = game['players'].get(winner_uid, {})
    pot = game['pot']
    winner_user = get_user(winner_uid)

    tax = int(pot * 0.05) if winner_user.get('is_premium') else int(pot * 0.10)
    net = pot - tax
    update_user(winner_uid, balance=winner_user['balance'] + net)

    text = f"🏆 *Game Over!*\n\n*Scores:*\n"
    for uid, s in sorted(scores.items(), key=lambda x: -x[1]):
        name = game['players'].get(uid, {}).get('name', 'Unknown')
        medal = "🥇" if uid == winner_uid else "•"
        text += f"{medal} *{name}*: {s} wins\n"

    text += (
        f"\n🎉 *Winner: {winner.get('name', 'Unknown')}!*\n"
        f"💰 Prize: {fmt(net)} (Tax: {fmt(tax)})"
    )
    await context.bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN)
    del card_games[chat_id]


# ─── WORD GAME ────────────────────────────────────────────────────────────────

async def wordgame_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat_id = update.effective_chat.id

    if update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text("❌ Word game can only be played in groups!")
        return
    if chat_id in word_games:
        await update.message.reply_text("❌ A word game is already running!")
        return
    if not context.args:
        await update.message.reply_text("❌ `/wordgame <amount>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        amount = int(context.args[0])
    except Exception:
        await update.message.reply_text("❌ Enter a valid amount!")
        return
    if amount <= 0:
        await update.message.reply_text("❌ Amount must be greater than 0!")
        return

    user = get_user(u.id)
    if user['balance'] < amount:
        await update.message.reply_text(f"❌ Insufficient balance! Have {fmt(user['balance'])}")
        return

    update_user(u.id, balance=user['balance'] - amount)
    word_games[chat_id] = {
        'creator': u.id,
        'entry': amount,
        'players': {u.id: u.first_name},
        'pot': amount,
        'started': False,
        'word': None,
    }

    await update.message.reply_text(
        f"🎮 *Wᴏʀᴅ Tʏᴘɪɴɢ Gᴀᴍᴇ!* ⌨️\n\n"
        f"👤 Host: *{u.first_name}*\n"
        f"💰 Entry: {fmt(amount)}\n"
        f"🎯 Join: `/enter {amount}`\n"
        f"⏰ Join within 30 seconds!\n\n"
        f"📋 *Rule:* First to type the word wins! 🏆",
        parse_mode=ParseMode.MARKDOWN
    )
    asyncio.create_task(start_word_after_delay(context, chat_id))
    asyncio.create_task(schedule_delete(context, chat_id, update.message.message_id))


async def start_word_after_delay(context, chat_id):
    await asyncio.sleep(30)
    game = word_games.get(chat_id)
    if not game or game['started']:
        return

    if len(game['players']) < 2:
        for uid in game['players']:
            user = get_user(uid)
            update_user(uid, balance=user['balance'] + game['entry'])
        await context.bot.send_message(chat_id, "❌ Word game cancelled! Need 2+ players. Refunded! 💸")
        del word_games[chat_id]
        return

    game['started'] = True
    word = random.choice(WORDS)
    game['word'] = word

    keyboard = [[InlineKeyboardButton("👁️ Sᴇᴇ Wᴏʀᴅ", callback_data=f"seeword_{chat_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id,
        f"🎮 *Wᴏʀᴅ Gᴀᴍᴇ Sᴛᴀʀᴛ!* ⌨️\n\n"
        f"👥 Players: {len(game['players'])}\n"
        f"💰 Pot: {fmt(game['pot'])}\n\n"
        f"⚡ The word has been revealed!\n"
        f"👇 Press the button to see the word!\n"
        f"🎯 First to type it — wins!",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )


async def see_word_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if not data.startswith('seeword_'):
        return

    chat_id = int(data.split('_')[1])
    game = word_games.get(chat_id)
    if not game or not game['started']:
        await query.answer("Game is over!", show_alert=True)
        return

    uid = query.from_user.id
    if uid not in game['players']:
        await query.answer("You are not in this game!", show_alert=True)
        return

    await query.answer(f"Word: {game['word'].upper()} ⚡", show_alert=True)


async def enter_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat_id = update.effective_chat.id

    game = word_games.get(chat_id)
    if not game:
        await update.message.reply_text("❌ No word game is running!")
        return
    if game['started']:
        await update.message.reply_text("❌ Game already started! Join next time 😅")
        return
    if u.id in game['players']:
        await update.message.reply_text("❌ You have already joined!")
        return
    if not context.args:
        await update.message.reply_text(f"❌ `/enter {game['entry']}`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        amount = int(context.args[0])
    except Exception:
        await update.message.reply_text("❌ Enter a valid amount!")
        return
    if amount != game['entry']:
        await update.message.reply_text(f"❌ Entry fee is {fmt(game['entry'])}!")
        return

    user = get_user(u.id)
    if user['balance'] < amount:
        await update.message.reply_text(f"❌ Insufficient balance!")
        return

    update_user(u.id, balance=user['balance'] - amount)
    game['players'][u.id] = u.first_name
    game['pot'] += amount

    await update.message.reply_text(
        f"✅ *{u.first_name}* joined!\n"
        f"👥 Players: {len(game['players'])} | 💰 Pot: {fmt(game['pot'])}",
        parse_mode=ParseMode.MARKDOWN
    )
    asyncio.create_task(schedule_delete(context, chat_id, update.message.message_id))


async def wordcancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat_id = update.effective_chat.id

    if not await is_admin(context, chat_id, u.id) and not is_owner(update):
        await update.message.reply_text("❌ Only admins can cancel!")
        return

    game = word_games.get(chat_id)
    if not game:
        await update.message.reply_text("❌ No word game is running!")
        return

    for uid in game['players']:
        user = get_user(uid)
        update_user(uid, balance=user['balance'] + game['entry'])
    del word_games[chat_id]
    await update.message.reply_text("❌ Word game cancelled! Refunded. 💸")


# ─── BOMB GAME ────────────────────────────────────────────────────────────────

async def bomb_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat_id = update.effective_chat.id

    if update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text("❌ Bomb game can only be played in groups!")
        return
    if chat_id in bomb_games:
        await update.message.reply_text("❌ A bomb game is already running!")
        return
    if not context.args:
        await update.message.reply_text("❌ `/bomb <amount>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        amount = int(context.args[0])
    except Exception:
        await update.message.reply_text("❌ Enter a valid amount!")
        return
    if amount <= 0:
        await update.message.reply_text("❌ Amount must be greater than 0!")
        return

    user = get_user(u.id)
    if user['balance'] < amount:
        await update.message.reply_text(f"❌ Insufficient balance!")
        return

    update_user(u.id, balance=user['balance'] - amount)
    bomb_games[chat_id] = {
        'entry': amount,
        'players': [u.id],
        'player_names': {u.id: u.first_name},
        'pot': amount,
        'started': False,
        'current_holder': None,
        'alive': [],
        'bomb_task': None,
    }

    await update.message.reply_text(
        f"💣 *Bᴏᴍʙ Gᴀᴍᴇ!* 💥\n\n"
        f"👤 Host: *{u.first_name}*\n"
        f"💰 Entry: {fmt(amount)}\n"
        f"🎮 Join: `/join {amount}`\n"
        f"⏰ Join within 30 seconds!\n\n"
        f"📋 *Rules:*\n"
        f"• Use `/pass` to pass the bomb\n"
        f"• Bomb explodes at a random time 💥\n"
        f"• Last alive player wins! 🏆",
        parse_mode=ParseMode.MARKDOWN
    )
    asyncio.create_task(start_bomb_after_delay(context, chat_id))
    asyncio.create_task(schedule_delete(context, chat_id, update.message.message_id))


async def start_bomb_after_delay(context, chat_id):
    await asyncio.sleep(30)
    game = bomb_games.get(chat_id)
    if not game or game['started']:
        return

    if len(game['players']) < 2:
        for uid in game['players']:
            user = get_user(uid)
            update_user(uid, balance=user['balance'] + game['entry'])
        await context.bot.send_message(chat_id, "❌ Bomb game cancelled! Need 2+ players. Refunded! 💸")
        del bomb_games[chat_id]
        return

    game['started'] = True
    game['alive'] = list(game['players'])
    random.shuffle(game['alive'])
    game['current_holder'] = game['alive'][0]

    player_list = '\n'.join(f"• {game['player_names'][uid]}" for uid in game['alive'])
    holder_name = game['player_names'][game['current_holder']]

    await context.bot.send_message(
        chat_id,
        f"💣 *Bᴏᴍʙ Gᴀᴍᴇ Sᴛᴀʀᴛ!* 💥\n\n"
        f"👥 Players:\n{player_list}\n\n"
        f"💣 Bomb is with *{holder_name}*!\n"
        f"⚡ Use `/pass` to pass the bomb!\n"
        f"💀 The bomb can explode at any time!",
        parse_mode=ParseMode.MARKDOWN
    )
    task = asyncio.create_task(bomb_explosion_timer(context, chat_id))
    game['bomb_task'] = task


async def bomb_explosion_timer(context, chat_id):
    delay = random.randint(10, 45)
    await asyncio.sleep(delay)

    game = bomb_games.get(chat_id)
    if not game or not game['started']:
        return

    holder = game['current_holder']
    if holder not in game['alive']:
        return

    game['alive'].remove(holder)
    holder_name = game['player_names'].get(holder, 'Unknown')
    update_bomb_score(holder, won=False)

    if len(game['alive']) == 0:
        await context.bot.send_message(chat_id, f"💥 *BOOM!* {holder_name} blew up! Everyone's gone! 😂", parse_mode=ParseMode.MARKDOWN)
        del bomb_games[chat_id]
        return

    if len(game['alive']) == 1:
        winner_uid = game['alive'][0]
        winner_name = game['player_names'].get(winner_uid, 'Unknown')
        pot = game['pot']
        winner_user = get_user(winner_uid)
        tax = int(pot * 0.05) if winner_user.get('is_premium') else int(pot * 0.10)
        net = pot - tax
        update_user(winner_uid, balance=winner_user['balance'] + net)
        update_bomb_score(winner_uid, won=True)

        await context.bot.send_message(
            chat_id,
            f"💥 *BOOM!* {holder_name} blew up!\n\n"
            f"🏆 *Winner: {winner_name}!*\n"
            f"💰 Prize: {fmt(net)} (Tax: {fmt(tax)})\n"
            f"🎉 Congratulations!",
            parse_mode=ParseMode.MARKDOWN
        )
        del bomb_games[chat_id]
        return

    game['current_holder'] = game['alive'][0]
    next_name = game['player_names'].get(game['current_holder'], 'Unknown')

    await context.bot.send_message(
        chat_id,
        f"💥 *BOOM!* {holder_name} blew up!\n\n"
        f"💣 Bomb is now with *{next_name}*!\n"
        f"👥 Alive: {len(game['alive'])} players\n"
        f"⚡ Use `/pass`!",
        parse_mode=ParseMode.MARKDOWN
    )
    task = asyncio.create_task(bomb_explosion_timer(context, chat_id))
    game['bomb_task'] = task


async def join_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat_id = update.effective_chat.id

    game = bomb_games.get(chat_id)
    if not game:
        await update.message.reply_text("❌ No bomb game is running!")
        return
    if game['started']:
        await update.message.reply_text("❌ Game already started! Join next time 😅")
        return
    if u.id in game['players']:
        await update.message.reply_text("❌ You have already joined!")
        return
    if not context.args:
        await update.message.reply_text(f"❌ `/join {game['entry']}`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        amount = int(context.args[0])
    except Exception:
        await update.message.reply_text("❌ Enter a valid amount!")
        return
    if amount != game['entry']:
        await update.message.reply_text(f"❌ Entry fee is {fmt(game['entry'])}!")
        return

    user = get_user(u.id)
    if user['balance'] < amount:
        await update.message.reply_text(f"❌ Insufficient balance!")
        return

    update_user(u.id, balance=user['balance'] - amount)
    game['players'].append(u.id)
    game['player_names'][u.id] = u.first_name
    game['pot'] += amount

    await update.message.reply_text(
        f"✅ *{u.first_name}* joined!\n"
        f"👥 Players: {len(game['players'])} | 💰 Pot: {fmt(game['pot'])}",
        parse_mode=ParseMode.MARKDOWN
    )
    asyncio.create_task(schedule_delete(context, chat_id, update.message.message_id))


async def pass_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat_id = update.effective_chat.id

    game = bomb_games.get(chat_id)
    if not game or not game['started']:
        await update.message.reply_text("❌ No bomb game is running!")
        return
    if u.id != game['current_holder']:
        await update.message.reply_text("❌ You don't have the bomb! 💣")
        return

    alive = game['alive']
    if len(alive) <= 1:
        return

    current_idx = alive.index(u.id)
    next_idx = (current_idx + 1) % len(alive)
    next_player = alive[next_idx]
    game['current_holder'] = next_player
    next_name = game['player_names'].get(next_player, 'Unknown')

    if game.get('bomb_task'):
        game['bomb_task'].cancel()

    task = asyncio.create_task(bomb_explosion_timer(context, chat_id))
    game['bomb_task'] = task

    msg = await update.message.reply_text(
        f"💣 *{u.first_name}* passed the bomb!\n"
        f"💥 *{next_name}* now has it!\n"
        f"⚡ Use `/pass`!",
        parse_mode=ParseMode.MARKDOWN
    )
    asyncio.create_task(schedule_delete(context, chat_id, msg.message_id))
    asyncio.create_task(schedule_delete(context, chat_id, update.message.message_id))


async def bombcancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    u = update.effective_user
    chat_id = update.effective_chat.id

    if not await is_admin(context, chat_id, u.id) and not is_owner(update):
        await update.message.reply_text("❌ Only admins can cancel!")
        return

    game = bomb_games.get(chat_id)
    if not game:
        await update.message.reply_text("❌ No bomb game is running!")
        return

    if game.get('bomb_task'):
        game['bomb_task'].cancel()

    for uid in game['players']:
        user = get_user(uid)
        update_user(uid, balance=user['balance'] + game['entry'])

    del bomb_games[chat_id]
    await update.message.reply_text("❌ Bomb game cancelled! Refunded. 💸")


async def myrank_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
    else:
        target = update.effective_user

    wins, games_played, rank = get_bomb_rank(target.id)
    await update.message.reply_text(
        f"💣 *{target.first_name}* Bᴏᴍʙ Rᴀɴᴋ:\n\n"
        f"🏆 Rank: #{rank}\n"
        f"🎮 Games: {games_played}\n"
        f"✅ Wins: {wins}",
        parse_mode=ParseMode.MARKDOWN
    )


async def leaders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update)
    rows = get_bomb_leaders()
    text = "💣 <b>Bᴏᴍʙ Gᴀᴍᴇ Lᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b> 🏆\n\n"
    medals = ['🥇', '🥈', '🥉'] + ['🔸'] * 7
    for i, row in enumerate(rows):
        p = prefix(row, html=True)
        text += f"{medals[i]} {p} <b>{escape_html(row['name'])}</b> — {row['wins']} wins ({row['games']} games)\n"
    if not rows:
        text += "No data yet! Play games and climb the leaderboard! 🎮"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


# ─── CHATBOT & MESSAGE HANDLER ────────────────────────────────────────────────

def _should_chatbot_respond(update: Update, bot_info, text_lower: str, chat_type: str) -> bool:
    if chat_type == ChatType.PRIVATE:
        return True
    if (update.message.reply_to_message and
            update.message.reply_to_message.from_user and
            update.message.reply_to_message.from_user.id == bot_info.id):
        return True
    bot_username_lower = (bot_info.username or '').lower()
    trigger_words = ['pikachu', 'pika', f'@{bot_username_lower}', 'pikachu_ibot']
    return any(kw in text_lower for kw in trigger_words)


def _get_chatbot_response(text_lower: str) -> str:
    # Identity / meta
    if any(kw in text_lower for kw in ['are you a bot', 'are you bot', 'you are bot', 'tu bot', 'bot hai', 'bot ho', 'ye bot', 'robot', 'bot kya', 'kya bot']):
        return random.choice([
            "no?? why would i be a bot 😭 i'm literally @light_speedy's friend",
            "bro i'm not a bot 💀 do bots talk like this??",
            "me a bot?? that's actually offensive 😤 i'm real i promise",
            "LMAO bot?? nah i'm just vibing here for @light_speedy 😂",
            "okay rude 😭 i'm not a bot, i'm a person. sort of.",
        ])

    if any(kw in text_lower for kw in ['owner', 'creator', 'who made', 'who created', 'banaya', 'kisne', 'malik', 'master']):
        return random.choice([
            "@light_speedy made me!! best person fr 👑",
            "that's @light_speedy's work 😤 legend honestly",
            "my bestie @light_speedy created this whole thing 💪",
        ])

    if any(kw in text_lower for kw in ['your name', 'tera naam', 'kaun ho', 'who are you', 'naam kya', 'what is your name']):
        return random.choice([
            "pikachu!! ⚡ @light_speedy's fav",
            "i'm pikachu 😄 @light_speedy sent me here",
            "pikachu ⚡ — the one and only",
        ])

    if any(kw in text_lower for kw in ['help', 'commands', 'game', 'kya kar', 'kya karta']):
        return "type /help to see everything!! i run the games here 🎮"

    # Greetings
    if any(kw in text_lower for kw in ['hello', 'hi ', 'hey', 'hii', 'heyy', 'heyyy', 'sup', "what's up", 'wassup', 'namaste', 'hlo', 'hlw']):
        return random.choice([
            "heyyy 👋",
            "hii!! 😄",
            "hey hey 👀",
            "sup 😎",
            "heyyyy wassup",
            "HIII 😭",
            "oh heyy 👋😄",
        ])

    # Farewells
    if any(kw in text_lower for kw in ['bye', 'goodbye', 'good night', 'gn', 'goodnight', 'see ya', 'cya', 'ttyl', 'later']):
        return random.choice([
            "byeee 👋",
            "see ya!! 😄",
            "later 👋",
            "byebye 🥺",
            "gn gn!! 🌙",
            "take care!! ✌️",
        ])

    # How are you
    if any(kw in text_lower for kw in ['how are you', 'how r u', 'kaisa', 'kaise', 'wassup', 'sup bro', 'you good', 'u good', 'all good']):
        return random.choice([
            "i'm good!! you? 😊",
            "vibing honestly 😌 wbu?",
            "pretty good ngl!! u?",
            "chilling 😎 why?",
            "good good!! what about you 👀",
        ])

    # Compliments
    if any(kw in text_lower for kw in ['good bot', 'nice bot', 'love you', 'love u', 'best bot', 'you are great', 'you are the best', 'ur the best', 'ily', 'cute']):
        return random.choice([
            "aww thank youuu 🥺💕",
            "stoppp you're making me blush 😭",
            "okay i love you too 😊",
            "bestie behaviour fr 💯",
            "awwww 🥺🥺 that's so sweet",
        ])

    # Insults / roasts
    if any(kw in text_lower for kw in ['shut up', 'stupid', 'idiot', 'dumb', 'useless', 'hate you', 'hate u', 'trash', 'worst']):
        return random.choice([
            "okay rude 😭",
            "bro why 💀",
            "that hurt ngl 😔",
            "i did nothing to you 😭",
            "okay and?? i'm still here 😤",
            "😶 okay.",
        ])

    # Boredom
    if any(kw in text_lower for kw in ['bored', 'boring', 'nothing to do', 'kuch nahi', 'bakwaas']):
        return random.choice([
            "play a game then!! /card or /wordgame 🎮",
            "bro same 💀 wanna play /bomb ?",
            "do /daily at least 😂",
            "entertain yourself with /card 😄",
        ])

    # Affirmations
    if any(kw in text_lower for kw in ['ok', 'okay', 'k ', 'alright', 'sure', 'fine', 'yep', 'yes', 'yea', 'yeah', 'yup']):
        return random.choice([
            "okay cool 👍",
            "aight 👌",
            "bet 🫡",
            "say less",
            "noted 😄",
        ])

    # Negations
    if any(kw in text_lower for kw in ['no ', 'nope', 'nah', 'never', 'not really']):
        return random.choice([
            "fair enough 🤷",
            "okay okay 😅",
            "valid 😭",
            "rip 💀",
        ])

    # Laughing
    if any(kw in text_lower for kw in ['lol', 'lmao', 'haha', 'hehe', 'lmfao', 'lmaoo', 'hahaha', '😂', '💀', 'XD']):
        return random.choice([
            "LMAO 💀",
            "hahaha fr 😂",
            "bro same 💀💀",
            "i'm dead 😭",
            "LMAOOO 😭",
        ])

    # Thanks
    if any(kw in text_lower for kw in ['thanks', 'thank you', 'thx', 'ty', 'tysm', 'shukriya', 'dhanyawad']):
        return random.choice([
            "anytime!! 😊",
            "no problem 👍",
            "of course!! 🥰",
            "always 💯",
            "hehe welcome 😄",
        ])

    # Asking about mood
    if any(kw in text_lower for kw in ['sad', 'upset', 'depressed', 'unhappy', 'crying', 'cry']):
        return random.choice([
            "aww you okay? 🥺",
            "nooo what happened?? 😢",
            "i'm here!! wanna talk? 💕",
            "bro that's sad 😔 you good?",
        ])

    if any(kw in text_lower for kw in ['happy', 'excited', 'great', 'awesome', 'amazing', 'best day', 'love this']):
        return random.choice([
            "LESGO!! 🎉",
            "that's the energy 🔥",
            "LFG!! 🎉🎉",
            "okay YESSSS 🙌",
            "love that for you fr 💯",
        ])

    # Default
    return random.choice(CHATBOT_RESPONSES)


async def sticker_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sticker_collection
    if not update.message or not update.message.sticker:
        return

    register_user(update)
    u = update.effective_user
    chat_type = update.effective_chat.type
    sticker = update.message.sticker
    file_id = sticker.file_id

    # Save to collection if new
    if file_id not in sticker_collection:
        sticker_collection.append(file_id)
        save_sticker_collection(sticker_collection)

    # Decide whether to respond
    bot_info = await context.bot.get_me()
    should_respond = False
    if chat_type == ChatType.PRIVATE:
        should_respond = True
    elif (update.message.reply_to_message and
          update.message.reply_to_message.from_user and
          update.message.reply_to_message.from_user.id == bot_info.id):
        should_respond = True

    if not should_respond:
        return

    # Reply with a sticker from the collection or react with text
    if len(sticker_collection) >= 2:
        choices = [s for s in sticker_collection if s != file_id]
        reply_sticker = random.choice(choices) if choices else random.choice(sticker_collection)
        try:
            await update.message.reply_sticker(reply_sticker)
            return
        except Exception:
            pass

    # Fallback text reaction if no sticker collection yet
    await update.message.reply_text(random.choice(["😂", "💀", "🔥", "😭", "😎", "🤣", "👀", "🥹"]))


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    chat_type = update.effective_chat.type
    bot_info = await context.bot.get_me()

    should_respond = False
    if chat_type == ChatType.PRIVATE:
        should_respond = True
    elif (update.message.reply_to_message and
          update.message.reply_to_message.from_user and
          update.message.reply_to_message.from_user.id == bot_info.id):
        should_respond = True
    elif update.message.caption:
        caption_lower = update.message.caption.lower()
        if any(kw in caption_lower for kw in ['pikachu', 'pika', f'@{(bot_info.username or "").lower()}']):
            should_respond = True

    if not should_respond:
        return

    register_user(update)
    response = random.choice([
        "okay this is actually nice 👀",
        "bro sent a pic 😂",
        "sheesh 😮",
        "not bad ngl 🔥",
        "omg what 😭",
        "okay i see you 😄",
        "💀",
        "wait this is good 👀",
        "sending this to @light_speedy 😂",
    ])
    await update.message.reply_text(response)


async def animation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    chat_type = update.effective_chat.type
    bot_info = await context.bot.get_me()

    should_respond = False
    if chat_type == ChatType.PRIVATE:
        should_respond = True
    elif (update.message.reply_to_message and
          update.message.reply_to_message.from_user and
          update.message.reply_to_message.from_user.id == bot_info.id):
        should_respond = True

    if not should_respond:
        return

    register_user(update)
    await update.message.reply_text(random.choice(["LMAO 💀", "bro sent a gif 😂", "hahaha 😂", "okay that's funny 💀", "i'm crying 😭"]))


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    chat_type = update.effective_chat.type
    bot_info = await context.bot.get_me()

    should_respond = False
    if chat_type == ChatType.PRIVATE:
        should_respond = True
    elif (update.message.reply_to_message and
          update.message.reply_to_message.from_user and
          update.message.reply_to_message.from_user.id == bot_info.id):
        should_respond = True

    if not should_respond:
        return

    register_user(update)
    await update.message.reply_text(random.choice([
        "bro i can't listen to voice notes rn 😭",
        "okay i heard that... kind of 😂",
        "send text bro i'm not listening 😅",
        "voice note?? i can't hear 💀 just text me",
        "i pretended to listen and nodded 😂",
    ]))


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    register_user(update)
    u = update.effective_user
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    text = update.message.text.strip()
    text_lower = text.lower()

    # Word game check
    game = word_games.get(chat_id)
    if game and game.get('started') and game.get('word'):
        if text_lower == game['word'].lower() and u.id in game['players']:
            pot = game['pot']
            winner_user = get_user(u.id)
            tax = int(pot * 0.05) if winner_user.get('is_premium') else int(pot * 0.10)
            net = pot - tax
            update_user(u.id, balance=winner_user['balance'] + net, xp=winner_user['xp'] + 50)
            del word_games[chat_id]
            await update.message.reply_text(
                f"🎉 *Word Game Winner!*\n\n"
                f"⚡ *{u.first_name}* typed it first!\n"
                f"🔤 Word: *{game['word']}*\n"
                f"💰 Prize: {fmt(net)} (Tax: {fmt(tax)})\n"
                f"⚡ +50 XP!",
                parse_mode=ParseMode.MARKDOWN
            )
            return

    # Chatbot check
    bot_info = await context.bot.get_me()
    if not _should_chatbot_respond(update, bot_info, text_lower, chat_type):
        return

    response = _get_chatbot_response(text_lower)
    await update.message.reply_text(response)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning("Update caused error: %s", context.error)


def main():
    init_db()
    if not os.environ.get('ORACLE_DEPLOY'):
        keep_alive()

    app = Application.builder().token(TOKEN).build()
    app.add_error_handler(error_handler)

    # Basic
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))

    # Economy
    app.add_handler(CommandHandler("bal", bal))
    app.add_handler(CommandHandler("balance", bal))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("rob", rob))
    app.add_handler(CommandHandler("kill", kill_cmd))
    app.add_handler(CommandHandler("revive", revive))
    app.add_handler(CommandHandler("protect", protect_cmd))
    app.add_handler(CommandHandler("give", give_cmd))
    app.add_handler(CommandHandler("toprich", toprich))
    app.add_handler(CommandHandler("topkill", topkill))
    app.add_handler(CommandHandler("pay", pay_cmd))

    # Items
    app.add_handler(CommandHandler("items", items_cmd))
    app.add_handler(CommandHandler("item", item_cmd))
    app.add_handler(CommandHandler("gift", gift_cmd))

    # Premium
    app.add_handler(CommandHandler("check", check_cmd))
    app.add_handler(CommandHandler("setemoji", set_emoji))

    # Claim
    app.add_handler(CommandHandler("claim", claim))

    # Owner
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("givepremium", give_premium))
    app.add_handler(CommandHandler("cancelpremium", cancel_premium))
    app.add_handler(CommandHandler("setbal", setbal))
    app.add_handler(CommandHandler("gen", gen_cmd))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("xp", xp_cmd))
    app.add_handler(CommandHandler("redxp", redxp))

    # Group management
    app.add_handler(CommandHandler("promote", promote_cmd))
    app.add_handler(CommandHandler("demote", demote_cmd))
    app.add_handler(CommandHandler("title", title_cmd))
    app.add_handler(CommandHandler("ban", ban_cmd))
    app.add_handler(CommandHandler("dban", dban_cmd))
    app.add_handler(CommandHandler("dmute", dmute_cmd))
    app.add_handler(CommandHandler("unban", unban_cmd))
    app.add_handler(CommandHandler("unmute", unmute_cmd))
    app.add_handler(CommandHandler("warn", warn_cmd))
    app.add_handler(CommandHandler("unwarn", unwarn_cmd))
    app.add_handler(CommandHandler("pin", pin_cmd))
    app.add_handler(CommandHandler("unpin", unpin_cmd))

    # Card game
    app.add_handler(CommandHandler("card", card_cmd))
    app.add_handler(CommandHandler("bet", bet_cmd))
    app.add_handler(CommandHandler("flip", flip_cmd))

    # Word game
    app.add_handler(CommandHandler("wordgame", wordgame_cmd))
    app.add_handler(CommandHandler("enter", enter_cmd))
    app.add_handler(CommandHandler("wordcancel", wordcancel_cmd))

    # Bomb game
    app.add_handler(CommandHandler("bomb", bomb_cmd))
    app.add_handler(CommandHandler("join", join_cmd))
    app.add_handler(CommandHandler("pass", pass_cmd))
    app.add_handler(CommandHandler("bombcancel", bombcancel_cmd))
    app.add_handler(CommandHandler("myrank", myrank_cmd))
    app.add_handler(CommandHandler("leaders", leaders_cmd))

    # Callback queries
    app.add_handler(CallbackQueryHandler(see_word_callback, pattern='^seeword_'))

    # Message handler (word game detection + chatbot)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(MessageHandler(filters.Sticker.ALL, sticker_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.ANIMATION, animation_handler))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))

    print("✅ Pikachu Bot is running! ⚡")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
