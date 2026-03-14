import discord
from discord.ext import commands, tasks
import schedule
import time

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
