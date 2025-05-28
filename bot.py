import discord
from discord.ext import commands
from config import DISCORD_TOKEN

class TheCoolerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix='!', intents=intents)
    
    async def setup_hook(self):
        await self.load_extension("cogs.basic")
        await self.load_extension("cogs.music")
        
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} commands.")
        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

if __name__ == '__main__':
    bot = TheCoolerBot()
    bot.run(DISCORD_TOKEN)
