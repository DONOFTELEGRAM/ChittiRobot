import importlib
import time
import re
import sys
from sys import argv
from typing import Optional

from SaitamaRobot import (
    ALLOW_EXCL,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    TOKEN,
    URL,
    WEBHOOK,
    SUPPORT_CHAT,
    dispatcher,
    StartTime,
    telethn,
    updater,
    pgram,
    ubot)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from SaitamaRobot.modules import ALL_MODULES
from SaitamaRobot.modules.helper_funcs.chat_status import is_user_admin
from SaitamaRobot.modules.helper_funcs.misc import paginate_modules
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown
from pyrogram import Client, idle

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


PM_START_TEXT = """
Hi, I'm [『Rajnii』](t.me/rajniirobot)!,
_A bot to manage your chats when you're offline._
_Make sure to read my "About" section to know how you can use me effectively!_
*Join Chatting Group - @RajniSpam!*
*Checkout Full Help menu by sending /help or click help button to know about my modules and usage*.
"""

buttons = [
    [
        InlineKeyboardButton(
            text="Add Rajnii to your group",
            url="t.me/RajniiRobot?startgroup=true")],
    [
        InlineKeyboardButton(
            text="About Me",
            callback_data="rajni_"),
        InlineKeyboardButton(
            text="Help section",
            callback_data="help_back"),
    ],
]



HELP_STRINGS = """
*『*[Help](https://telegra.ph/file/d40481cb215f983a3fb9c.jpg) *section:』*

Hey there! My name is *{}*.
I'm here Active to help your admins manage their groups with My Advanced Modules!
Have a look at the following for an idea of some of the things I can help you with.
*Main commands available :*
 • /start : Starts me, can be used to check i'm alive or no...
 • /help : PM's you this message.
 • /help <module name> : PM's you info about that module.

*Need help? head to @RajniSupportChat*
Click on the buttons below to get documentation about specific modules!
 • /settings :
   • in PM: will send you your settings for all supported modules.
   • in a group: will redirect you to pm, with all that chat's settings.
{}
And the following:
""".format(
    dispatcher.bot.first_name,
    "" if not ALLOW_EXCL else "\nAll commands can either be used with / or !.\n",
)

SAITAMA_IMG = "https://telegra.ph/file/0c8c80cc3df5c6a340448.jpg"

DONATE_STRING = """*『Rajnii』* is hosted on Heroku free server yet,
so it doesn't need any donations for now,
But if you want to donate my developer you can,
You can also DM my developer to ask about donation.
• [Gpay](https://pay.google.com)
*UPI ID* - `dhruv040.04@okaxis`
• By Scanning the [BHIM UPI QR CODE](https://telegra.ph/file/4b6abf3199adf23c7e8f3.jpg) below
by your payment application.

*What we do with donations?*
» _donations will help us to run Rajni
 on a paid server by which
 Rajni will work faster than before!_
» _donations will help us to improve Rajni
 with more useful and fun modules._
» _these donations will also help us
 to help others, those who really need support._
"""
BOT_PIC = "https://telegra.ph/file/586f1921ec80a73836c55.mp4"
IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("SaitamaRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=False,
        reply_markup=keyboard,
    )


@run_async
def test(update: Update, context: CallbackContext):
    # print(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)

@run_async
def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "Here is the help for *{}* module:\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="★Home★", callback_data="rajni_back"),
                      InlineKeyboardButton(text="★Back★", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")))

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")))

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")))

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass

@run_async
def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="★Back★", callback_data="help_back"),
                          InlineKeyboardButton(text="★Home★", callback_data="rajni_back")]]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            update.effective_message.reply_video(
                caption=BOT_PIC,
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        update.effective_message.reply_text(
            "I'm awake already!\n<b>Haven't slept since:</b> <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
        )



# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


@run_async
def rajni_about_callback(update, context):
    query = update.callback_query
    if query.data == "rajni_":
        query.message.edit_text(
            text=f"""*『*[About](https://telegra.ph/file/54be2e85bd0b185c74db2.jpg) *section:』*
                 \nI'm *『Rajnii』*, a powerful & moduler group management bot built to help your admins and you to manage your group easily.
                 \n*Here's a Shortlist what I can do.*
                 \n\n• I can restrict users.
                 \n• I can greet users with customizable welcome messages and even set a group's rules.
                 \n• I have an advanced anti-flood system.
                 \n• I can warn users until they reach max warns, with each predefined actions such as ban, mute, kick, etc.
                 \n• I have a note keeping system, blacklists, and even predetermined replies on certain keywords.
                 \n• I check for admin’s permissions before executing any command and more stuffs.
                 \n• I have more useful and fun modules too.
                 \n• I can chat with users by using [Kuki AI](https://kuki-api.tk).
                 \n• [Click here](https://youtube.com/playlist?list=PLR1ul39qY-jfgtjUdzTxV2On8O5OWbgTw) to know about my basic modules on [YouTube](https://www.youtube.com).
                 \n• Rajnii’s reposiratory is private, anyone can’t fork, if you want base Repository [Click here](https://github.com/AnimeKaizoku/SaitamaRobot) | don't come to us for asking Rajni's Repo otherwise you'll get direct ban.
                 \n• Reach my Support Links at [here](https://t.me/RajniSupportChat/3).
                 \n\n*If you have any question about me, let our team help you at @{SUPPORT_CHAT}*.
                 \n *Thanks for using me :),* [Click here](https://t.me/RajniUpdates/97) *to Share & Support us*💙""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
                [
                 [InlineKeyboardButton(text="Credits 👨‍💻", callback_data="credits_"),
                  InlineKeyboardButton(text="Support 👨‍✈️", callback_data="support_"),
                  InlineKeyboardButton(text="Manual 📚", callback_data="manual_")],
                 [InlineKeyboardButton(text="Terms And Conditions 📄", callback_data="tandc_")],
                 [InlineKeyboardButton(text="★Home★", callback_data="rajni_back"),
                  InlineKeyboardButton(text="★Help★", callback_data="help_back")],
                ]))
    elif query.data == "rajni_back":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )

@run_async
def rajni_manual_callback(update, context):
    query = update.callback_query
    if query.data == "manual_":
        query.message.edit_text(
            text=f"""*『*[Manual](https://telegra.ph/file/8e8fb6982ef9e4f0cd799.jpg) *section:』*
                 \nHere is the help how to use me with my best performance, follow the steps below!
                 \n\n• First add me to a group...
                 \n» Click the “Add me” button and select a group where you want me to help you and your admins :).
                 \n• Promote me with all admin rights to let me get in actions!.
                 \n• You can know about module related helps by help menu, Click “Help” to open, select a module to know about it.
                 \n• Now start learning and try to use me better!, You can get all support and help related to me at @{SUPPORT_CHAT}.""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
                [
                 [InlineKeyboardButton(text="｢Add me」", url="t.me/RajniiRobot?startgroup=true"),
                  InlineKeyboardButton(text="｢About」", callback_data="rajni_")],
                 [InlineKeyboardButton(text="｢Admin Setup」", callback_data="adminsetup_"),
                  InlineKeyboardButton(text="｢Anti-Spam Setup」", callback_data="antispamsetup_")],
                 [InlineKeyboardButton(text="★Home★", callback_data="rajni_back"),
                  InlineKeyboardButton(text="★Help★", callback_data="help_back")],
                ]))

def admin_setup(update, context):
    query = update.callback_query
    if query.data == "adminsetup_":
        query.message.edit_text(
            text="""*｢ Admin Setup 」*

                 \n• To avoid slowing down, Rajnii caches admin rights for each user. This cache lasts about 10 minutes; this may change in the future. This means that if you promote a user manually (without using the /promote command), Rajnii will only find out ~10 minutes later.
                 \n• If you want to update them immediately, you can use the `/admincache` command,thta'll force Rajnii to check who the admins are again and their permissions
                 \n• If you are getting a message saying:
`You must be this chat administrator to perform this action!`
                 \n• This has nothing to do with Rajnii’s rights; this is all about your permissions as an admin. Rajnii respects admin permissions; if you do not have the Ban Users permission as a telegram admin, you won't be able to ban users with Rajnii. Similarly, to change Rajnii settings, you need to have the Change group info permission.
                 \n• The message very clearly says that you need these admin rights; Rajnii already have.""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [InlineKeyboardButton(text="Manual", callback_data="manual_"),
                  InlineKeyboardButton(text="About", callback_data="rajni_")],
                 [InlineKeyboardButton(text="★Home★", callback_data="rajni_back"),
                  InlineKeyboardButton(text="★Help★", callback_data="help_back")],
                ]))


def antispam_setup(update, context):
    query = update.callback_query
    if query.data == "antispamsetup_":
        query.message.edit_text(
            text="""*｢ Anti-Spam Setup 」*
                 \n\n\n*« Anti-Spam »*
                 \n• `/antispam <on/off/yes/no>`: Change antispam security settings in the group, or return your current settings(when no arguments).
This helps protect you and your groups by removing spam flooders as quickly as possible.

                 \n\n*« Anti-Flood »*
                 \n• `/setflood <int/'no'/'off'>`: enables or disables flood control
                 \n• `/setfloodmode <ban/kick/mute/tban/tmute> <value>`: Action to perform when user have exceeded flood limit. ban/kick/mute/tmute/tban
Antiflood allows you to take action on users that send more than x messages in a row. Exceeding the set flood will result in restricting that user.

                 \n\n*« Blacklist »*
                 \n• `/addblacklist <triggers>`: Add a trigger to the blacklist. Each line is considered one trigger, so using different lines will allow you to add multiple triggers.
                 \n• `/blacklistmode <off/del/warn/ban/kick/mute/tban/tmute>`: Action to perform when someone sends blacklisted words.
Blacklists are used to stop certain triggers from being said in a group. Any time the trigger is mentioned, the message will immediately be deleted. A good combo is sometimes to pair this up with warn filters!

                 \n\n*« Reports »*
                 \n• `/reports <on/off>`: Change report setting, or view current status.
                 \n  × If done in pm, toggles your status.
                 \n  × If in chat, toggles that chat's status.
If someone in your group thinks someone needs reporting, they now have an easy way to call all admins.

                 \n\n*« Locks »*
                 \n• `/lock <type>`: Lock items of a certain type (not available in private)
                 \n• `/locktypes`: Lists all possible locktypes
The locks module allows you to lock away some common items in the telegram world; the bot will automatically delete them!

                 \n\n*« Warns »*
                 \n• `/addwarn <keyword> <reply message>`: Sets a warning filter on a certain keyword. If you want your keyword to be a sentence, encompass it with quotes, as such: /addwarn "very angry" This is an angry user. 
                 \n• `/warn <userhandle>`: Warns a user. After 3 warns, the user will be banned from the group. Can also be used as a reply.
                 \n• `/strongwarn <on/yes/off/no>`: If set to on, exceeding the warn limit will result in a ban. Else, will just kick.
If you're looking for a way to automatically warn users when they say certain things, use the /addwarn command.

                 \n\n*« Captcha »*
                 \n• `/captcha <off/soft/strong>`: All users that join, get muted
A button gets added to the welcome message for them to unmute themselves. This proves they aren't a bot! soft - restricts users ability to post media for 24 hours. strong - mutes on join until they prove they're not bots.

                 \n\n*« Federations »*
                 \n• Join @RajniiRobot’s official Federation by sending the below command to your group (You shouldn't be Anonymous there, You should be owner of the group to do this).
 [Click here](https://telegram.me/RajniiRobot?start=ghelp_federations) to know what a federation do.
 `/joinfed 48b40c38-d23b-49a9-b064-531ac228df74`
                 \n• Join our Rose bot Federation [TIAF] • A as same as above one.
 `/joinfed 26e460c0-7819-4bdf-acd0-b4aee506563d`.""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [InlineKeyboardButton(text="Manual", callback_data="manual_"),
                  InlineKeyboardButton(text="About", callback_data="rajni_")],
                 [InlineKeyboardButton(text="★Home★", callback_data="rajni_back"),
                  InlineKeyboardButton(text="★Help★", callback_data="help_back")],
                ]))


@run_async
def rajni_support_callback(update, context):
    query = update.callback_query
    if query.data == "support_":
        query.message.edit_text(
            text=f"""*『*[Support](https://telegra.ph/file/3c90f6fc89c72d529e60f.jpg) *section:』*
                     \n*Just Click the link below as it’s mentioned:*

                     \n\n• Join Support chat - @{SUPPORT_CHAT}.
                     \n• Join Updates here - @RajniUpdates.
                     \n• Global Events here - @RajniGlobal.
                     \n• Join Spam/Appeal chat - @RajniSpam.
                     \n• Join Developers chat - @SanatanRakshaDevelopers.""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
                [
                 [InlineKeyboardButton(text="About 📑", callback_data="rajni_")],
                 [InlineKeyboardButton(text="★Home★", callback_data="rajni_back"),
                  InlineKeyboardButton(text="★Help★", callback_data="help_back")],
                ]))

@run_async
def rajni_credits_callback(update, context):
    query = update.callback_query
    if query.data == "credits_":
        query.message.edit_text(
            text=f"""*『*[Developers](https://telegra.ph/file/e8037324894de412039a4.jpg) *section:』*
                     \n\n*• Main developer   - @itzzzyashu*
                     \n*• Normal Updates   - @sawada*
                     \n*• New modules      - @flasho_gacha*
                     \n*• Updated modules  - @Awesome_RJ_official*
                     \n*• Base code        - @SonOfLars*""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
                [
                 [InlineKeyboardButton(text="About 📑", callback_data="rajni_")],
                 [InlineKeyboardButton(text="★Home★", callback_data="rajni_back"),
                  InlineKeyboardButton(text="★Help★", callback_data="help_back")],
                ]))


@run_async
def rajni_tandc_callback(update, context):
    query = update.callback_query
    if query.data == "tandc_":
        query.message.edit_text(
            text=f"""*『*[T&C](https://telegra.ph/file/7812d8db02304724334da.jpg) *section:』*
                     \n*The Terms and Conditions are as follows:*

                     \n\n• We respect everyone's privacy & we never collect Sensitive data from groups.
                     \n• Rajnii is one of the safest, Stable, and Moduler telegram bot.
                     \n• Messages between users and Rajnii is End to End Encrypted!
                     \n• NSFW content spammers always get Permanent Global Ban in Rajnii Database.
                     \n• Be Active on your chats, if someone spamming your group, you can use report feature & you can also report us about that on @RajniSpam to appeal a Gban/Fban.
                     \n• Make sure antiflood is enabled, so nobody can flood/spam your group.
                     \n• Please don't spam bot commands or buttons weather in pm or in groups, it can make Rajnii Slower to respond and if we blacklist them who spams Rajni’s buttons or commands, Hence Rajni will ignore thier existance.
                     \n• Global appeals for Rajnii? Read the [criteria](https://t.me/RajniGlobal/402) first.
                     \n Appeal Global Actions at [RajniSpam Appeal/Off-topic chat](t.me/RajniSpam).
                     \n• We only stores User ID, Usernames, Name only, which is needed bot to respond to any user.
                     \n\n_Terms & Conditions can be changed anytime, please check once a month._""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
                [
                 [InlineKeyboardButton(text="About 📑", callback_data="rajni_")],
                 [InlineKeyboardButton(text="★Home★", callback_data="rajni_back"),
                  InlineKeyboardButton(text="★Help★", callback_data="help_back")],
                ]))

@run_async
def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text="Help",
                        url="t.me/{}?start=ghelp_{}".format(
                            context.bot.username, module))
                ]]))
            return
        update.effective_message.reply_text(
            "Contact me in PM to get the list of possible commands.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    text="Help",
                    url="t.me/{}?start=help".format(context.bot.username))
            ]]))
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = "Here is the available help for the *{}* module:\n".format(HELPABLE[module].__mod_name__) \
               + HELPABLE[module].__help__
        send_help(
            chat.id, text,
            InlineKeyboardMarkup(
                [InlineKeyboardButton(
                        text="★Home★",
                        callback_data="rajni_back"),
                 InlineKeyboardButton(
                        text="★Back★",
                        callback_data="help_back")]))

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join("*{}*:\n{}".format(
                mod.__mod_name__, mod.__user_settings__(user_id))
                                   for mod in USER_SETTINGS.values())
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN)

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN)

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?"
                .format(chat_name),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)))
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN)


@run_async
def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(escape_markdown(chat.title),
                                                                                     CHAT_SETTINGS[module].__mod_name__) + \
                   CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text="Back",
                        callback_data="stngs_back({})".format(chat_id))
                ]]))

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id)))

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id)))

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)))

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message == "Message is not modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message can't be deleted":
            pass
        else:
            LOGGER.exception("Exception in settings buttons. %s",
                             str(query.data))


@run_async
def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text="Settings",
                        url="t.me/{}?start=stngs_{}".format(
                            context.bot.username, chat.id))
                ]]))
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)


@run_async
def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)

        if OWNER_ID != 254318997 and DONATION_LINK:
            update.effective_message.reply_text(
                "Thanks for supporting us!😘"
                "[Our BHIM UPI QR](https://telegra.ph/file/4b6abf3199adf23c7e8f3.jpg)",
                parse_mode=ParseMode.MARKDOWN)

    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True)

            update.effective_message.reply_text(
                "I've PM'ed you about donating to my creator!")
        except Unauthorized:
            update.effective_message.reply_text(
                "Contact me in PM first to get donation information.")


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendMessage(f"@{SUPPORT_CHAT}", "I am now online!")
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support chat, go and check!")
        except BadRequest as e:
            LOGGER.warning(e.message)



  # INPUT HANDLERS
    # Main Handlers
    test_handler = CommandHandler("test", test)
    start_handler = CommandHandler("start", start)

    # About Callbacks
    about_callback_handler = CallbackQueryHandler(rajni_about_callback, pattern=r"rajni_")
    term_condition_handler = CallbackQueryHandler(rajni_tandc_callback, pattern=r"tandc_")
    support_callback_handler = CallbackQueryHandler(rajni_support_callback, pattern=r"support_")
    credits_callback_handler = CallbackQueryHandler(rajni_credits_callback, pattern=r"credits_")
    manual_callback_handler = CallbackQueryHandler(rajni_manual_callback, pattern=r"manual_")
    admin_setup_handler = CallbackQueryHandler(admin_setup, pattern=r"adminsetup_")
    antispam_setup_handler = CallbackQueryHandler(antispam_setup, pattern=r"antispamsetup_")

    # Help Handlers
    help_handler = CommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(
        help_button, pattern=r"help_.*")
    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(
        settings_button, pattern=r"stngs_")
    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(Filters.status_update.migrate,
                                     migrate_chats)


   # OUTPUT HANDLERS 
    # Main Handlers
    # dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(settings_handler)

    # Info Callbacks
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(term_condition_handler)
    dispatcher.add_handler(credits_callback_handler)
    dispatcher.add_handler(support_callback_handler)
    dispatcher.add_handler(manual_callback_handler)
    dispatcher.add_handler(admin_setup_handler)
    dispatcher.add_handler(antispam_setup_handler)

    # Help Handlers
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)
    dispatcher.add_error_handler(error_callback)



    if WEBHOOK:
        time.sleep(3)
        LOGGER.info("[RAJNII] • SRN • Using webhooks.")
        time.sleep(1)
        LOGGER.info("[RAJNII] • SRN • Connection Successful!")
        time.sleep(1)
        LOGGER.info(f"[RAJNII] • SRN • Rajni deployed, check @{SUPPORT_CHAT}")
        updater.start_webhook(listen="127.0.0.1", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        time.sleep(3)
        LOGGER.info("[RAJNII] • SRN • Long polling")
        time.sleep(1)
        LOGGER.info("[RAJNII] • SRN • Connection Successful!")
        time.sleep(1)
        LOGGER.info(f"[RAJNII] • SRN • Rajni deployed, check @{SUPPORT_CHAT}")
        updater.start_polling(timeout=15, read_latency=4)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()

try:
    ubot.start()
except BaseException:
    print("[RAJNII] • Userbot Error ! Please add a STRING_SESSION get it from https://repl.it/@SpEcHiDe/GenerateStringSession - Telethon String Session")
    sys.exit(1)

if __name__ == '__main__':
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pgram.start()
    main()
    idle()
