import discord
import csv
import csvhelper
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands
from datetime import datetime

# client = discord.Client()
bot = commands.Bot(command_prefix = '!')
channel_id=880988016582217751


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

    #initializing scheduler
    scheduler = AsyncIOScheduler()

    #sends "Your Message" at 12PM and 18PM (Local Time)
    scheduler.add_job(func, CronTrigger(second="27")) 

    #starting the scheduler
    scheduler.start()

async def func():
    await bot.wait_until_ready()
    c = bot.get_channel(channel_id)
    await c.send("Your Message")



@bot.command()
async def test(ctx):
    print('We haveasdsa logged in as {0.user}'.format(bot))
    await ctx.send('testtt')

@bot.command()
async def addmember(ctx, *args):
    f = csvhelper.read_file()
    for arg in args:        
        csvhelper.add_column(f, arg)
    csvhelper.write_file(f)

@bot.command()
async def paid(ctx, *args):
    time = datetime.now().strftime('%B') + str(datetime.today().year)
    f = csvhelper.read_file()
    for arg in args:
        try:
            csvhelper.mark_paid(f, arg, time, 'Y')
        except ValueError:
            print('not a vliad person')
            await ctx.send('not a valid person')
    csvhelper.write_file(f)

@bot.command()
async def notpaid(ctx, *args):
    time = datetime.now().strftime('%B') + str(datetime.today().year)
    f = csvhelper.read_file()
    for arg in args:
        try:
            csvhelper.mark_paid(f, arg, time, 'N')
        except ValueError:
            print('not a vliad person')
            await ctx.send('not a valid person')
    csvhelper.write_file(f)

@bot.command()
async def whohasntpaid(ctx):
    time = datetime.now().strftime('%B') + str(datetime.today().year)
    f = csvhelper.read_file()
    try:
        people = csvhelper.hasntpaid(f, time)
        await ctx.send('people haven\'t paid: ' + ', '.join(people))
    except StopIteration:
        await ctx.send('It is a new month, no one has paid yet')



bot.run("ODgwOTg3ODM0MjQzMjQ0MDUz.YSmR2w.6NEX5uy47he0GQzygXIlchrQ9XM")