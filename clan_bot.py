import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime, timedelta

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

def setup_database():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events
                (id INTEGER PRIMARY KEY,
                name TEXT,
                date TEXT)''')
    conn.commit()
    conn.close()
setup_database

@bot.event
async def on_ready():
    print(f'{bot.user} is online and ready')
    setup_database()
    daily_reminder.start()

@bot.command()
async def hello(ctx):
    await ctx.send("LastZ Clan Bot is here! Ready to remind you of clan events!")

@bot.command()
async def addevent(ctx,event_name, date_time):
    try:
        event_name = datetime.strptime(date_time, '%Y-%m-%d %H:%M')
        conn = sqlite3.connect('events.bd')
        c= conn.cursor()
        c.execute("INSERT INTO events (name, date) VALUES (?, ?)",
                  (event_name, date_time))
        conn.commit()
        conn.close()

        await ctx.send(f"✅ Event added!\n Event: {event_name}\n Date: {date_time}")
    except ValueError:
        await ctx.send("Wrong date format! Use: !addevent EventName 2026-03-21 20:00")

@bot.command()
async def events(ctx):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute("SELECT id, name, date FROM events ORDER BY date")
    all_events = c.fetchall()
    conn.close()

    if len(clan_events) == 0:
        await ctx.send("No upcoming events! Use !addevent to add one.")
    else:
        message = "**Upcoming Clan Events:**\n"
        for event in all_events:
            message += f"{event[0]}. {event[1]} - {event[2]}\n"
        await ctx.send(message)

@bot.command()
async def nextevent(ctx):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute("SELECT id, name, date FROM events ORDER BY date LIMIT 1")
    event = c.fetchone()
    conn.close()

    if event is None:
        await ctx.send("No upcoming events! Use !addevent to add one.")
    else:
        await ctx.send(f"**Next Event:**\n {event[1]}\n {event[2]}")

@bot.command()
async def removeevent(ctx, event_id:int):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute("SELECT name, date FROM events WHERE id = ?", (event_id,))
    event = c.fetchone()

    if event is None:
        await ctx.send("Event not found! Use !events to see the list.")
    else:
        c.execute("DELETE FROM events WHERE id = ?", (event_id,))
        conn.commit()
        await ctx.send(f"Removed: **{event[0]}** - {event[1]}")
    conn.close()
@bot.command()
async def clearevents(ctx):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute("DELETE FROM events")
    conn.commit()
    conn.close()
    await ctx.send("All events have been cleared!")

@bot.command(name='help')
async def help_command(ctx):
    await ctx.send("""
 **LastZ Clan Bot Commands:**

**!addevent [name] [date] [time]**
   Add a new clan event
   Example: !addevent Raid 2026-03-21 20:00

 **!events**
   Show all upcoming events

 **!nextevent**
   Show the next upcoming event

 **!removeevent [id]**
   Remove an event by its number
   Example: !removeevent 1

 **!clearevents**
   Clear all events

 **!help**
   Show this help message""")
                  
@tasks.loop(hours=24)
async def daily_reminder():
    channel = discord.utils.get(bot.get_all_channels(), name='general')
    if channel:
        conn = sqlite3.connect('events.db')
        c = conn.cursor()
        c.execute("SELECT id, name, date FROM events ORDER BY date")
        all_events = c.fetchall()
        conn.close()

        if len(all_events) > 0:
            message = "⚔️ **Daily Clan Events Reminder!**\n"
            for event in all_events:
                message += f"{event[0]}. {event[1]} — {event[2]}\n"
            await channel.send(message)

@daily_reminder.before_loop
async def before_reminder():
    await bot.wait_until_ready()
 
bot.run(TOKEN)
