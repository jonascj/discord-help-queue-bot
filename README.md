# Discord Bot: Help Queue
A simple (quick and dirty) bot which handles a simple (fifo) queue 
for help / support / private discussion requests.

One or more admin members can dequeue members from the queue 
to offer help / support / private discussion in an orderly fashion.

# Installation 

## Clone the repo
```
git clone https://github.com/jonascj/discordhelp-queue-bot.git
```

or download files in some other manner from the repo.

## Install dependencies 
```
pip install -r reqs.txt
```
or
```
pip install discord.py python-dotenv
```
## Create an `.env` file for configuration
Make a copy of `.env.template` called `.env`:
```
cp .env.template .env
```
This is the configuration for the bot

## Create a Discord application 
Go to <https://discordapp.com/developers/applications>,
login with an discordapp.com user
and follow the steps as indicated in the screenshot below:
![Screenshot of discordapp.com application creation](docs/discord-create-application.png)

## Add a bot to the application
![Screenshot of adding a bot to a Discord app](docs/discord-add-bot.png)

## Bot token
Copy the bot token and add it to your `.env` file:
```
DISCORD_TOKEN=<your-token-here>
```
![Screenshot of obtaining bot token](docs/discord-bot-token.png)

## OAuth2 URL
Obtain an OAuth2 URL used to invite your bot to a server / guild.

Follow the steps as indicated in the screenshot below: 
![Screenshot of obtaining oauth2 url](docs/discord-bot-oauth-link.png)

In step 3 you need to select the following permissions: 
* `Send Messages`
* `Move Members` (optional, needed automatically move
members to the same voice channel as the dequeuing admin)

## Invite your bot to your server/guild
1. Visit the copied OAuth2 URL (`https://discordapp.com/api/oauth2/auth...`)
in your browser.

2. Login the user account used to create your guild/server
and select the server you wish to add the bot to.

If you login as a user which has created no servers
and does not have *Manage Server* permission on any other servers
the *Select a server* dropdown menu will be empty.

![Screenshot of adding bot to server](docs/discord-bot-add-to-server.png)

## Configuring admins
You could start your bot at this point (`python help_queue_bot.py`)
but no admins would be configured.
Members would be able to join the queue, 
but noone would be able to dequeue them.

### By user-id
1. Enable Developer Mode in the Discord App 
to gain access to the `Copy ID`-feature.
![Screenshot of enabling developer mode](docs/discord-dev-mode.png)

2. Right-click on any user's username or portrait/icon
and select `Copy ID`
![Screenshot of enabling developer mode](docs/discord-copy-id.png)

3. Add the ID to the `.env` file
```
ADMIN_USER_IDS=<id1>,<id2>
``` 

### By role names
1. Add a role to your server called `queue-admin` or whatever you wish.
2. Assign this role to all users on your server who should be able to
administrate the queue.
3. Add the role name to your `.env` file:
```
ADMIN_ROLE_NAME=<role1>,<role2>
```

## Start the bot
Finally start the Python bot:
```
python help_queue_bot.py
```



