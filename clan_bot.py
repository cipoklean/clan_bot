import discord
from discord.ext import commands, tasks
import schedule
import time
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

if TOKEN is None:
    print("Error: Token not found!")
else:
    print("Token loaded successfully!")

clan_events = []

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is online and ready')

@bot.command()
async def hello(ctx):
    await ctx.send("LastZ Clan Bot is here! Ready to remind you of clan events!")

@bot.command()
async def addevent(ctx,event_name, date, time):
    clan_events.append({
        'event': event_name,
        'date': date,
        'time': time
    })
    await ctx.send(f"✅ Event added!\n Event: {event_name}\n Date: {date}\n Time: {time}")


@bot.command()
async def events(ctx):
    if len(clan_events) == 0:
        await ctx.send("**Upcoming Clan Events:**\n No events yet. Use !addevent to add one!")
    else:
        message = "**Upcoming Clan Events:**\n"
        for i, event in enumerate(clan_events, 1):
            message += f"{i}. {event['event']} - {event['date']} at {event['time']}\n"
        await ctx.send(message)

@bot.command()
async def removeevent(ctx, number:int):
    if number < 1 or number > len(clan_events):
        await ctx.send("Invaild event number! use !events to see the list.")
    else:
        removed = clan_events.pop(number - 1)
        await ctx.send(f"removed: **{removed['event']}** - {removed['date']} at {removed['time']}")

@bot.command()
async def clearevents(ctx):
    clan_events.clear()
    await ctx.send("All events have been cleared!")

@bot.command()
async def nextevent(ctx):
    if len(clan_events) == 0:
        await ctx.send(" No upcoming events! Use !addevent to add one.")
    else:
        event = clan_events[0]
        await ctx.send(f" **Next Event:**\n📌 {event['event']}\n📅 {event['date']}\n⏰ {event['time']}")
@bot.command(name='help')
async def help_command(ctx):
    await ctx.send("""
⚔️ **LastZ Clan Bot Commands:**

**!addevent [name] [date] [time]**
   Add a new clan event
   Example: !addevent Raid Saturday 8PM

 **!events**
   Show all upcoming events

 **!nextevent**
   Show the next upcoming event
                   
 **!nextevent**
   Show the next upcoming event

 **!removeevent [number]**
   Remove an event by its number
   Example: !removeevent 1

 **!clearevents**
   Clear all events

 **!help**
   Show this help message""")
                   
@tasks.loop(hours=24)
async def daily_reminder():
    channel = discord.utils.get(bot.get_all_channels(), name='general')
    if channel and len(clan_events) > 0:
        message = "**Daily Clan Events Reminder!**\n"
        for i, event in enumerate(clan_events, 1):
            message += f"{i}. {event['event']} - {event['date']} at {event['time']}\n"
        await channel.send(message)

@daily_reminder.before_loop
async def before_reminder():
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    print(f'{bot.user} is online and ready!')
    daily_reminder.start()    
bot.run(TOKEN)
