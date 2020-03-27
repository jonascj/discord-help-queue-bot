from datetime import datetime
import json
import logging
import os
import sys

import discord
from discord.ext import commands
import dotenv

# Load .evn variables 
dotenv.load_dotenv()

# Logging
LOG_LVL = os.getenv('LOG_LVL')
log = logging.getLogger(__name__)
if not LOG_LVL:
    LOG_LVL = 'DEBUG'

h = logging.StreamHandler(sys.stdout)
h.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log.addHandler(h)
log.setLevel(LOG_LVL)

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
ADMIN_USER_IDS = [int(s.strip()) for s in os.getenv('ADMIN_USER_IDS').split(',')]
ADMIN_ROLE_NAMES = [s.strip() for s in os.getenv('ADMIN_ROLE_NAMES').split(',')]

if not TOKEN:
    log.error('`DISCORD_TOKEN` must be set in .env file')
    sys.exit()

if not ADMIN_USER_IDS and not ADMIN_ROLE_NAMES:
    log.error('Either `ADMIN_USER_IDS`, `ADMIN_ROLE_NAMES` or both '
              'must be set in .env file')
    sys.exit()


# Create bot
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')

# Queue file/disk handling
DISK_FILE = 'help_queue.json'
try:
    with open(DISK_FILE, 'r') as f:
        help_queue = json.load(f)
        log.info('Loaded existing queue from file/disk')
except:
    help_queue = {}
    log.info('Created new empty queue')

def save_to_disk():
    with open('help_queue.json', 'w') as f:
        json.dump(help_queue, f)


# Bot helper functions
def get_guild_queue(ctx):
    key = '{}#{}'.format(ctx.guild.name,ctx.guild.id)
    if key not in help_queue:
        help_queue[key] = []
    return help_queue[key]


def get_user_name(user):
    if user.nick:
        # User has a server/guild nick set, use that
        return user.nick
    else:
        # Otherwise just use the user's account namt
        return user.name


def auth_admin(user):
    if user.id in ADMIN_USER_IDS:
        return True

    for r in user.roles:
        if r in ADMIN_ROLE_NAMES:
            return True

    return False
    




@bot.event
async def on_ready():
    log.info('Bot logged in as `%s` (id %s)', bot.user, bot.user.id)
    log.info('Member of the following servers/guilds:')
    for guild in bot.guilds:
        log.info('  %s', guild.name)



@bot.command(name='qu', aliases=['needhelp'], help='Queue up for help')
async def queue_up(ctx, msg=""):
            
    queue = get_guild_queue(ctx)
    for entry in queue:
        if entry['author_id'] == ctx.author.id:
            await ctx.send('{} You are already in the queue'.
                            format(ctx.author.mention))
            return

    entry = {'name': get_user_name(ctx.author),
             'author_id': ctx.author.id,
             'datetime': datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'),
             'msg': msg} 

    queue.append(entry)

    await ctx.send('{} You queued up for help'
                   '(position in queue: {})'
                   .format(ctx.author.mention, len(queue)))

    # Heads-up to queuing member about being first in line already
    if len(queue) == 1:
        try:
            await ctx.author.send('You\'re next in line, be ready for '
                                  'help / support / discussion '
                                  '(consider joining a voice channel!).')
        except:
            log.info('Failed to direct message member `%s` heads-up '
                     'about being first in line upon queuing',
                     get_user_name(ctx.author))
    save_to_disk()



@bot.command(name='qs', aliases=['show'], help='Show the queue')
async def queue_show(ctx):
    queue = get_guild_queue(ctx)
    now = datetime.now()
    
    embed = discord.Embed(title='Queue', colour = discord.Colour.blue())
    if len(queue) == 0:
        value='The queue is empty!'
    else:
        entries = []
        for entry in queue:
            joined = datetime.strptime(entry['datetime'], '%Y-%m-%d %H:%M:%S') 
            wait_min = (now-joined).seconds / 60

            if entry['msg']:
                entries.append('**{}** *({:.0f} min)*: {}'
                               .format(entry['name'], wait_min, entry['msg']))
            else:
                entries.append('**{}** *({:.0f} min)*'
                               .format(entry['name'], wait_min))
        value='\n'.join(entries)

    name = 'Users in the queue ({})'.format(len(queue))
    embed.add_field(name=name, value=value, inline=False)

    await ctx.send(embed=embed)



@bot.command(name='ql', aliases=['nvm'], help='Leave the help queue')
async def queue_leave(ctx):
    queue = get_guild_queue(ctx)
    for i, entry in enumerate(queue):
        if entry['author_id'] == ctx.author.id:
            del queue[i]
            await ctx.send('{} You left the queue'
                           .format(ctx.author.mention))
            return 

    await ctx.send('{} You are not in the queue and therefor can not leave it'
                   .format(ctx.author.mention))

    save_to_disk()



@bot.command(name='qe', help='Empty the queue (admin)')
async def queue_empty(ctx):
    if auth_admin(ctx.author):
        queue = get_guild_queue(ctx)
        queue.clear()
        await ctx.send('{} You emptied the queue'.format(ctx.author.mention))
    else:
        log.warning('Member `%s` (id %s) not authorized to empty queue', 
                    get_user_name(ctx.author), ctx.author.id)
        await ctx.send('{} Permission denied'.format(ctx.author.mention))

    save_to_disk()
    


@bot.command(name='qn', aliases=['next'], help='Help the next in line (admin)')
async def queue_next(ctx, message=""):
    if not auth_admin(ctx.author):
        log.warning('Member `%s` (id %s) not authorized to dequeue', 
                    get_user_name(ctx.author), ctx.author.id)
        await ctx.send('{} Permission denied'.format(ctx.author.mention))
        return

   
    # Dequeue next member (in queue)
    queue = get_guild_queue(ctx)
    if len(queue) == 0:
        await ctx.send('The queue is empty, nobody is requesting help!')
        return
    else:
        _next = queue.pop(0) # FIFO queue
        next_member = discord.utils.get(ctx.guild.members,id=_next['author_id'])

    if not next_member:
        await ctx.send('**{}** is not online or has left the server'
                       .format(_next['name']))
        return
    
    # Alert the next member
    try:
        await next_member.send('It is your turn to receive help/support '
                               'and/or discuss!')
    except:
        log.info('Unable to alert next member `%s`', get_user_name(next_member))

        await ctx.send('{} It is your turn to receive help/support '
                       'and/or discuss!'
                       .format(next_member.mention))


    # Move member to admin voice channel (if are connected to a voice channel)
    if ctx.author.voice and next_member.voice:
        try:
            await next_member.move_to(ctx.author.voice.channel,
                            reason='To facilitate help/support/discussion')
        except:
            log.info('Failed to move `{}` to voice channel of `{}`'
                     .format(get_user_name(next_member), get_user_name(ctx.author)))

    else:
        await ctx.send('{} {} Failed to move you to the same voice channel, '
                       'you will have to find each other manually'
                       .format(ctx.author.mention, next_member.mention))

    
    # Heads-up to (next) next member (now at the front of the queue)
    if len(queue) == 0:
        return
        
    _nextnext = queue[0] # Do not dequeue
    try:
        nextnext_member = discord.utils.get(ctx.guild.members,
                                            id=_nextnext['author_id'])

        await nextnext_member.send('You\'re next in line, be ready for '
                                   'help / support / discussion '
                                   '(consider joining a voice channel!).')
    except:
        log.info('Unable to send heads-up to `%s`',_nextnext['name'])

    

@bot.command(name="devdump", hidden=True)
async def devdump(ctx):
    log.info('## Dev dump ##')
    log.info('ctx.author.nick: %s', ctx.author.nick)
    log.info('ctx.author.name: %s', ctx.author.name)
    log.info('str(ctx.author): %s', str(ctx.author))
    log.info('ctx.author.mention: %s', ctx.author.mention)


@bot.command(name='help')
async def help(ctx):

    about_text = ('A simple bot which handles a simple (fifo) queue '
                 'for help / support / private discussion requests.\n\n'
                 'One or more admin members can dequeue members from the queue '
                 'to offer help / support / private discussion '
                 'in an orderly fashion.')

    embed = discord.Embed(colour = discord.Colour.blue())
    embed.set_author(name='Help')
    embed.add_field(name='About', value=about_text, inline=False)
                          
    embed.add_field(name='`!qu [msg]` | `!needhelp [msg]`',
                    value=('Queues you up for help with an optional message. '
                           'Quote messages with space, e.g. *!qu "what ever"*.'),
                    inline=False)

    embed.add_field(name='`!ql` | `!nvm`',
                    value='Leave the help queue',
                    inline=False)

    embed.add_field(name='`!qs` | `!show`',
                    value='Show the queue',
                    inline=False)

    embed.add_field(name='`!qn`|`!next` (admin)',
                    value='Help the next in line',
                    inline=False)

    embed.add_field(name='`!qe` (admin)',
                    value='Empty the queue for this server/guild',
                    inline=False)

    await ctx.send(embed=embed)

try:
    bot.run(TOKEN)
except discord.errors.LoginFailure:
    log.error('Bot login failed, improper/invalid token')
    sys.exit()

