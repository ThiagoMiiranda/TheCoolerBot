from discord.ext import commands
from utils.voice_validation import validate_voice
from music.player import MusicPlayer

class Music(commands.Cog):
    '''Cog that handles music playback and queue management.'''
    def __init__(self, bot):
        self.bot = bot
        self.player = MusicPlayer(bot)
    
    @commands.command()
    async def join(self, ctx):
        if not await validate_voice(ctx):
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
        if not await validate_voice(ctx, require_bot_connected=True):
            return

        voice_client = ctx.voice_client
        await voice_client.disconnect()
        await ctx.send(f"👋 Leaving **{voice_client.channel.name}**. Stay cool. 😎")
    
    @commands.command()
    async def play(self, ctx, url: str):
        author_voice = ctx.author.voice
        bot_voice = ctx.voice_client

        if author_voice is None:
            await ctx.send("You must be in a voice channel first.")
            return
        
        if bot_voice is None:
            await author_voice.channel.connect()
        else:
            if bot_voice.channel != author_voice.channel:
                await ctx.send("You must be in the same voice channel as The Cooler Bot.")
                return
        
        await self.player.add_and_maybe_play(ctx, url)
    
    @commands.command(name="queue")
    async def show_queue(self, ctx):
        guild_id = ctx.guild.id

        now_playing = self.player.get_current(guild_id)
        upcoming = self.player.get_queue(guild_id)

        if not now_playing and not upcoming:
            await ctx.send("📭 The queue is currently empty.")
            return
        
        message = ""

        if now_playing:
            message += f"🎧 **Now playing:** {now_playing['title']}\n\n"
        
        if upcoming:
            message += f"🎶 **Upcoming songs:**\n"
            for i, track in enumerate(upcoming, start=1):
                message += f"{i}. {track['title']} (added by {track['requested_by']})\n"
        
        await ctx.send(message)
    
    @commands.command()
    async def skip(self, ctx):
        if not await validate_voice(ctx, require_bot_connected=True):
            return
        
        voice_client = ctx.voice_client

        if not voice_client.is_playing():
            await ctx.send("There's no music playing to skip. 😕")
            return
        
        skipper = ctx.author.display_name
        await self.player.skip(ctx)
        await ctx.send(f"⏭️ **{skipper}** skipped the current song.")
    
    @commands.command()
    async def pause(self, ctx):
        if not await validate_voice(ctx, require_bot_connected=True):
            return
        
        voice_client = ctx.voice_client

        if not voice_client.is_playing():
            await ctx.send("There's no music to pause. 😕")
            return
        
        self.player.pause(ctx)
        await ctx.send(f"⏸️ Music paused by **{ctx.author.display_name}**.")
    
    @commands.command()
    async def resume(self, ctx):
        if not await validate_voice(ctx, require_bot_connected=True):
            return
        
        voice_client = ctx.voice_client

        if not voice_client.is_paused():
            await ctx.send("The music is not paused. 🤔")
            return
        
        self.player.resume(ctx)
        await ctx.send(f"▶️ Music resumed by **{ctx.author.display_name}**.")
    
    @commands.command()
    async def clear(self, ctx):
        if not await validate_voice(ctx, require_bot_connected=True):
            return
        
        guild_id = ctx.guild.id

        if not self.player.has_next(guild_id):
            await ctx.send("The queue is already empty.")
            return
        
        await self.player.clear(guild_id)
        await ctx.send(f"🧹 Queue cleared by **{ctx.author.display_name}**.")

async def setup(bot):
    await bot.add_cog(Music(bot))
