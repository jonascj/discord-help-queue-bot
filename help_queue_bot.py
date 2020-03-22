import os
from datetime import datetime

from discord.ext import commands
import dotenv

dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ADMIN_USER_IDS = [int(s.strip()) for s in os.getenv('ADMIN_USER_IDS').split(',')]
ADMIN_ROLE_NAMES = [s.strip() for s in os.getenv('ADMIN_ROLE_NAMES').split(',')]

bot = commands.Bot(command_prefix='!')

help_queue = {}

def get_guild_queue(context):
    key = (context.guild.id, context.guild.name)
    if key not in help_queue:
        help_queue[key] = []
    return help_queue[key]

def get_user_name(context):
    if context.author.nick != '':
        return context.author.nick
    else:
        return context.author.name

def auth_admin(context):
    if context.author.id in ADMIN_USER_IDS:
        return True
    
    for r in context.author.roles:
        if r in ADMIN_ROLE_NAMES:
            return True

    return False

    

@bot.event
async def on_ready():
    print('Bot logged in as {0.user}'.format(bot))


@bot.group(aliases=['q'], help='Queue management', invoke_without_command=True)
async def queue(c):
    await c.send('Please provide a subcommand, type `!help queue` for help')
    

@queue.group(pass_context=True)
async def show(c):
    q = get_guild_queue(c)
    now = datetime.now()

    output = 'Queue ({})\n'.format(len(q))
    for entry in q:
        wait_sec = (now-entry['datetime']).seconds
        line = '{} ({:.0f} min)'.format(entry['name'], 
                                          wait_sec/60)
        output += '    ' + line + '\n'

    await c.send(output)


@queue.group(pass_context=True)
async def empty(c):
    if auth_admin(c):
        q = get_guild_queue(c)
        q.clear()
    else:
        await c.send('Permission denied')

        

@queue.group(help='Places you in the help queue')
async def enter(c):
    q = get_guild_queue(c)
    for e in q:
        if e['author_id'] == c.author.id:
            await c.send('You are already in the queue {}'.format(get_user_name(c)))
            return

    entry = {'name': get_user_name(c),
             'author_id': c.author.id,
             'datetime': datetime.now(),
             'msg': c.message.content} 

    q.append(entry)

    await c.send('Queued {} for help (queue length: {})'.format(c.author.name, len(q)))


@bot.command(help='Places you in the help queue')
async def needhelp(c):
    await enter.invoke(c)


@queue.group(help='Removes you from the help queue')
async def leave(c):
    q = get_guild_queue(c)
    for e in q:
        if e['author_id'] == c.author.id:
            await c.send('You are already in the queue {}'.format(get_user_name(c)))
            return


bot.run(TOKEN)
