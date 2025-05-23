import discord
from discord.ext import commands
from config import DISCORD_TOKEN

class TheCoolerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix='!', intents=intents)
    
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        await self.load_extension("cogs.basic")
        await self.load_extension("cogs.music")

if __name__ == '__main__':
    bot = TheCoolerBot()
    bot.run(DISCORD_TOKEN)
