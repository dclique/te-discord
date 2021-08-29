import discord
import csv
import csvhelper
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands
from datetime import datetime

bot = commands.Bot(command_prefix = '!')

channel_id=os.environ["CHANNEL_ID"]
role=os.environ["ADMIN_ROLE"]
csvhelper.filename = os.environ["CSV_FILENAME"]
token = os.environ["ACCESS_TOKEN"]

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

    #initializing scheduler
    scheduler = AsyncIOScheduler()

    #scheduler.add_job(monthly_reminder, CronTrigger(day=3)) 
    scheduler.add_job(weekly_reminder, CronTrigger(day_of_week=6, hour=17))
    scheduler.add_job(debug_to_console, CronTrigger(hour=0))
    #starting the scheduler
    scheduler.start()


async def monthly_reminder():
    await bot.wait_until_ready()
    c = bot.get_channel(channel_id)
    await c.send("Reminder to pay for this month")

async def weekly_reminder():
    await bot.wait_until_ready()
    c = bot.get_channel(channel_id)
    people = csvhelper.hasntpaid(f, time)
    if (len(people) > 0):
        await c.send('Weekly reminder - the following people haven\'t paid: ' + ', '.join(people))

async def debug_to_console():
    f = csvhelper.read_raw()
    raw = csvhelper.dump_string(f)
    print(raw)


@bot.event
async def on_command_error(ctx, e):
    if isinstance(e, commands.MissingRole):
        return
    else:
        raise e


@bot.command()
async def debug(ctx):
    await debug_to_console()


@bot.command()
async def test(ctx):
    print('We haveasdsa logged in as {0.user}'.format(bot))
    print(ctx.message.author.id)
    await ctx.send('testtt')

@bot.command()
@commands.has_role(role)
async def addmember(ctx, *args):
    added = []
    notadded = []
    if len(args) > 0:
        f = csvhelper.read_file()
        for arg in args:
            try:
                csvhelper.add_column(f, arg)
                added.append(arg)
            except ValueError:
                notadded.append(arg)

        csvhelper.write_file(f)

        if len(added) == 1:
            await ctx.send('Added a new member: ' + ''.join(added))
        if len(added) > 1:
            await ctx.send('Added new members: ' + ', '.join(added))
        if len(notadded) == 1:
            await ctx.send(''.join(notadded) + ' already exists')
        if len(notadded) > 1:
            await ctx.send(', '.join(notadded) + ' already exist')

@bot.command()
@commands.has_role(role)
async def deletemember(ctx, *args):
    deleted = []
    notdeleted = []
    if len(args) > 0:
        f = csvhelper.read_file()
        for arg in args:
            try:
                csvhelper.delete_column(f, arg)
                deleted.append(arg)
            except ValueError:
                notdeleted.append(arg)
        csvhelper.write_file(f)
        if len(deleted) == 1:
            await ctx.send('Deleted member: ' + ''.join(deleted))
        if len(deleted) > 1:
            await ctx.send('Deleted members: ' + ', '.join(deleted))
        if len(notdeleted) == 1:
            await ctx.send(''.join(notdeleted) + ' does not exist')
        if len(notdeleted) > 1:
            await ctx.send(', '.join(notdeleted) + ' do not exist')


@bot.command()
@commands.has_role(role)
async def paid(ctx, *args):
    paid = []
    invalid = []
    if len(args) > 0:
        time = datetime.now().strftime('%B') + str(datetime.today().year)
        f = csvhelper.read_file()
        for arg in args:
            try:
                csvhelper.mark_paid(f, arg, time, 'Y')
                paid.append(arg)
            except ValueError:
                invalid.append(arg)
        csvhelper.write_file(f)
        if len(paid) > 0:
            await ctx.send(f"{', '.join(paid)} marked as paid for {datetime.now().strftime('%B')} {str(datetime.today().year)}")
        if len(invalid) == 1:
            await ctx.send(''.join(invalid) + ' is not a valid member')
        if len(invalid) > 1:
            await ctx.send(', '.join(invalid) + ' are not valid members')

@bot.command()
@commands.has_role(role)
async def notpaid(ctx, *args):
    paid = []
    invalid = []
    if len(args) > 0:
        time = datetime.now().strftime('%B') + str(datetime.today().year)
        f = csvhelper.read_file()
        for arg in args:
            try:
                csvhelper.mark_paid(f, arg, time, 'N')
                paid.append(arg)
            except ValueError:
                invalid.append(arg)
        csvhelper.write_file(f)
        if len(paid) > 0:
            await ctx.send(f"{', '.join(paid)} marked as not paid for {datetime.now().strftime('%B')} {str(datetime.today().year)}")
        if len(invalid) == 1:
            await ctx.send(''.join(invalid) + ' is not a valid member')
        if len(invalid) > 1:
            await ctx.send(', '.join(invalid) + ' are not valid members')

@bot.command()
async def whohasntpaid(ctx):
    time = datetime.now().strftime('%B') + str(datetime.today().year)
    f = csvhelper.read_file()
    try:
        people = csvhelper.hasntpaid(f, time)
        await ctx.send(f"These people haven\'t paid for {datetime.now().strftime('%B')} {str(datetime.today().year)}: {', '.join(people)}")
    except StopIteration:
        await ctx.send('It is a new month, no one has paid yet')

bot.run(token)