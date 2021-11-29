import os

import datetime
from typing import List

import requests
from YoneRobot import TIME_API_KEY, dispatcher
from YoneRobot.events import register
from YoneRobot import tbot
from telethon import types
from telethon.tl import functions
from YoneRobot.conf import get_str_key 
from YoneRobot.modules.disable import DisableAbleCommandHandler
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, run_async


TIME_API_KEY = get_str_key("TIME_API_KEY", required=False)

async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


def generate_time(to_find: str, findtype: List[str]) -> str:
    data = requests.get(
        f"http://api.timezonedb.com/v2.1/list-time-zone"
        f"?key={TIME_API_KEY}"
        f"&format=json"
        f"&fields=countryCode,countryName,zoneName,gmtOffset,timestamp,dst"
    ).json()

    for zone in data["zones"]:
        for eachtype in findtype:
            if to_find in zone[eachtype].lower():
                country_name = zone["countryName"]
                country_zone = zone["zoneName"]
                country_code = zone["countryCode"]

                if zone["dst"] == 1:
                    daylight_saving = "Yes"
                else:
                    daylight_saving = "No"

                date_fmt = r"%d-%m-%Y"
                time_fmt = r"%H:%M:%S"
                day_fmt = r"%A"
                gmt_offset = zone["gmtOffset"]
                timestamp = datetime.datetime.now(
                    datetime.timezone.utc
                ) + datetime.timedelta(seconds=gmt_offset)
                current_date = timestamp.strftime(date_fmt)
                current_time = timestamp.strftime(time_fmt)
                current_day = timestamp.strftime(day_fmt)

                break

    try:
        result = (
            f"<b>🌍Country :</b> <code>{country_name}</code>\n"
            f"<b>⏳Zone Name :</b> <code>{country_zone}</code>\n"
            f"<b>🗺Country Code :</b> <code>{country_code}</code>\n"
            f"<b>🌞Daylight saving :</b> <code>{daylight_saving}</code>\n"
            f"<b>🌅Day :</b> <code>{current_day}</code>\n"
            f"<b>⌚Current Time :</b> <code>{current_time}</code>\n"
            f"<b>📆Current Date :</b> <code>{current_date}</code>"
        )
    except BaseException:
        result = None

    return result


@register(pattern="^/datetime ?(.*)")
async def _(event):
    if event.fwd_from:
        return
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        else:
            return

    gay = event.pattern_match.group(1)

    try:
        query = gay
    except BaseException:
        await event.reply("Provide a country name/abbreviation/timezone to find.")
        return

    send_message = await event.reply(
        f"Finding timezone info for <b>{query}</b>", parse_mode="html"
    )

    query_timezone = query.lower()
    if len(query_timezone) == 2:
        result = generate_time(query_timezone, ["countryCode"])
    else:
        result = generate_time(query_timezone, ["zoneName", "countryName"])

    if not result:
        await send_message.edit(
            f"Timezone info not available for <b>{query}</b>", parse_mode="html"
        )
        return

    await send_message.edit(result, parse_mode="html") 
    
 
def gettime(update: Update, context: CallbackContext):
    message = update.effective_message

    try:
        query = message.text.strip().split(" ", 1)[1]
    except:
        message.reply_text("Provide a country name/abbreviation/timezone to find.")
        return
    send_message = message.reply_text(
        f"Finding timezone info for <b>{query}</b>", parse_mode=ParseMode.HTML
    )

    query_timezone = query.lower()
    if len(query_timezone) == 2:
        result = generate_time(query_timezone, ["countryCode"])
    else:
        result = generate_time(query_timezone, ["zoneName", "countryName"])

    if not result:
        send_message.edit_text(
            f"Timezone info not available for <b>{query}</b>\n"
            '<b>All Timezones:</b> <a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">List here</a>',
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return

    send_message.edit_text(
        result, parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )


TIME_HANDLER = DisableAbleCommandHandler("time", gettime)

dispatcher.add_handler(TIME_HANDLER)





__mod_name__ = "ᴅᴀᴛᴇ ᴛɪᴍᴇ"
__help__ = """Use This Commend to watch country time in chat 
 ❍ /time (country name)
 - /datetime <timezone>: Get the present date and time information
**You can check out this [link](https://timezonedb.com/time-zones) for the available timezones**
""" 
__command_list__ = ["time"]
__handlers__ = [TIME_HANDLER]
