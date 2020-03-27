# Discord Bot: Help Queue
A simple (quick and dirty) bot which handles a simple (fifo) queue 
for help / support / private discussion requests.

One or more admin members can dequeue members from the queue 
to offer help / support / private discussion in an orderly fashion.

# Installation 
1. Clone repo `git clone https://github.com/jonascj/discordhelp-queue-bot.git`
or download files in some other manner

2. Install dependencies discord.py and python-dotenv
```
pip install -r reqs.txt
```
or
```
pip install discord.py python-dotenv
```

3. Create an application at <https://discordapp.com/developers/applications>
![Screenshot of discordapp.com application creation](docs/discord-create-application.png)

4. Add a bot to the application
![Screenshot of adding a bot to a Discord app](docs/discord-add-bot.png)

5. Obtain the bot token and add it to your `.env` file
![Screenshot of obtaining bot token](docs/discord-bot-token.png)

6. Obtain an OAuth2 URL to invite your bot to a Discord server/guild.

The bot needs the following permissions (step 3):
* `Send Messages`
* `Move Members` (optional, needed automatically move
members to the same voice channel as the dequeuing admin)

![Screenshot of obtaining both oauth invite link](docs/discord-bot-oauth-link.png)

