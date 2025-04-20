import discord
from discord.ext import commands
import yt_dlp

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def validate_voice(self, ctx, require_bot_connected=False):
        author_voice = ctx.author.voice
        bot_voice = ctx.voice_client

        if author_voice is None:
            await ctx.send("You must be in a voice channel first.")
            return False
        
        if require_bot_connected and not bot_voice:
            await ctx.send("The Cooler Bot isn't in a voice channel.")
            return False
        
        if require_bot_connected and author_voice.channel != bot_voice.channel:
            await ctx.send("You must be in the same voice channel as The Cooler Bot.")
            return False
        
        return True
    
    @commands.command()
    async def join(self, ctx):
        if not await self.validate_voice(ctx):
            return

        voice_channel = ctx.author.voice.channel
        voice_client = ctx.voice_client

        if voice_client is None:
            await voice_channel.connect()
        else:
            await voice_client.move_to(voice_channel)

        await ctx.send(f"Joined **{voice_channel.name}**!")

    @commands.command()
    async def leave(self, ctx):
        if not await self.validate_voice(ctx, require_bot_connected=True):
            return

        voice_client = ctx.voice_client
        await voice_client.disconnect()
        await ctx.send(f"👋 Leaving **{voice_client.channel.name}**. Stay cool. 😎")
    
    @commands.command()
    async def play(self, ctx, url: str):
        pass

async def setup(bot):
    await bot.add_cog(Music(bot))
