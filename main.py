import discord
import csv
import csvhelper
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands
from datetime import datetime

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix = '!', intents=intents)

channel_id=os.environ["CHANNEL_ID"]
guild_id=os.environ["GUILD_ID"]
role=os.environ["ADMIN_ROLE"]
dues_file = os.environ["DUES_FILE"]
members_file = os.environ["MEMBERS_FILE"]
token = os.environ["ACCESS_TOKEN"]


class Members:
    def __init__(self):
        self.membermap = None

    async def get_members(self):
        if self.membermap == None:
            self.membermap = {}
            f = csvhelper.read_file(members_file)
            people = f[1]
            for person in people:
                user = await bot.fetch_user(people[person])
                username = str(user)
                self.membermap.update({person: username})
        return self.membermap

    def clear(self):
        self.membermap = None


memberObj = Members()

def add_member(nickname, username, userid):
    f = csvhelper.read_file(members_file)
    f[0].append(nickname)
    people = f[1]
    people.update({nickname: userid})
    csvhelper.write_file(f, members_file)
    memberObj.clear()

def delete_member(nickname):
    f = csvhelper.read_file(members_file)
    try:
        f[0].remove(nickname)
        people = f[1]
        people.pop(nickname)
        csvhelper.write_file(f, members_file)
        memberObj.clear()
    except ValueError:
        return

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
    time = datetime.now().strftime('%B') + str(datetime.today().year)
    f = csvhelper.read_file(dues_file)
    c = bot.get_channel(channel_id)
    people = csvhelper.hasntpaid(f, time)

    if (len(people) > 0):
        peoplemention = []
        peoplemap = await memberObj.get_members()
        for person in people:
            if person in peoplemap:
                userid = bot.get_guild(guild_id).get_member_named(peoplemap[person]).id
                peoplemention.append('<@'+ str(userid)+'>')
            else:
                peoplemention.append(person)
        await c.send(f"Weekly reminder - the following people haven\'t paid for {datetime.now().strftime('%B')} {str(datetime.today().year)}: {', '.join(peoplemention)}")


async def debug_to_console():
    f = csvhelper.read_raw(dues_file)
    g = csvhelper.read_raw(members_file)
    raw = csvhelper.dump_string(f)
    raw2 = csvhelper.dump_string(g)
    print(raw)
    print(raw2)


@bot.event
async def on_message(message):
    if str(message.channel.id) == channel_id:
        await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, e):
    if isinstance(e, commands.MissingRole):
        return
    else:
        raise e


@bot.command()
async def debug(ctx):
    print(await memberObj.get_members())
    await debug_to_console()


@bot.command()
@commands.has_role(role)
async def addmember(ctx, *args):
    if len(args) > 0 and len(args) < 3:
        f = csvhelper.read_file(dues_file)
        if args[0] in f[0]:
            members = await memberObj.get_members()
            if args[0] not in members:
                if len(args) == 2:
                    memberid = ctx.guild.get_member_named(args[1]).id                
                    add_member(args[0], args[1], memberid)
                    await ctx.send(f'Associated {args[0]} to <@{str(memberid)}>')
                    return
            await ctx.send('Member ' + args[0] + ' already exists')
            return
        else:
            try:
                csvhelper.add_column(f, args[0])
                if len(args) == 2:
                    memberid = ctx.guild.get_member_named(args[1]).id                
                    add_member(args[0], args[1], memberid)
                csvhelper.write_file(f, dues_file)
                await ctx.send('Added new member: ' + args[0])
            except ValueError:
                await ctx.send('Member ' + args[0] + ' already exists')


@bot.command()
@commands.has_role(role)
async def deletemember(ctx, *args):
    members = await memberObj.get_members()
    if len(members) == 1:
        await ctx.send('There\'s only one discord tag associated member left, cannot delete them because the world will end!')
    if len(args) == 1:
        f = csvhelper.read_file(dues_file)

        try:
            csvhelper.delete_column(f, args[0])
            csvhelper.write_file(f, dues_file)
            delete_member(args[0])
            await ctx.send('Deleted member: ' + args[0])
        except ValueError:
            await ctx.send('Member ' + args[0] + ' doesn\'t exist')


@bot.command()
@commands.has_role(role)
async def paid(ctx, *args):
    paid = []
    invalid = []
    if len(args) > 0:
        time = datetime.now().strftime('%B') + str(datetime.today().year)
        f = csvhelper.read_file(dues_file)
        for arg in args:
            try:
                csvhelper.mark_paid(f, arg, time, True)
                paid.append(arg)
            except ValueError:
                invalid.append(arg)
        csvhelper.write_file(f, dues_file)
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
        f = csvhelper.read_file(dues_file)
        for arg in args:
            try:
                csvhelper.mark_paid(f, arg, time, False)
                paid.append(arg)
            except ValueError:
                invalid.append(arg)
        csvhelper.write_file(f, dues_file)
        if len(paid) > 0:
            await ctx.send(f"{', '.join(paid)} marked as not paid for {datetime.now().strftime('%B')} {str(datetime.today().year)}")
        if len(invalid) == 1:
            await ctx.send(''.join(invalid) + ' is not a valid member')
        if len(invalid) > 1:
            await ctx.send(', '.join(invalid) + ' are not valid members')


@bot.command()
async def whohasntpaid(ctx):
    time = datetime.now().strftime('%B') + str(datetime.today().year)
    f = csvhelper.read_file(dues_file)
    try:
        people = csvhelper.hasntpaid(f, time)
        if len(people) == 0:
            await ctx.send('Everyone has paid for this month')
            return
        peoplemention = []
        peoplemap = await memberObj.get_members()
        for person in people:
            if person in peoplemap:
                userid = ctx.guild.get_member_named(peoplemap[person]).id
                peoplemention.append('<@'+ str(userid)+'>')
            else:
                peoplemention.append(person)
        await ctx.send(f"These people haven\'t paid for {datetime.now().strftime('%B')} {str(datetime.today().year)}: {', '.join(peoplemention)}")
    except StopIteration:
        await ctx.send('It is a new month, no one has paid yet')

bot.run(token)