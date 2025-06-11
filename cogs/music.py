from discord import app_commands
from discord.ext import commands
from utils.voice_validation import validate_voice
from utils.message import safe_send
from utils.embeds import queue_embed
from utils.queue_paginator import QueuePaginator
from music.player import MusicPlayer
import discord

class Music(commands.Cog):
    '''Cog that handles music playback and queue management.'''
    def __init__(self, bot):
        self.bot = bot
        self.player = MusicPlayer(bot)
    
    @commands.hybrid_command(description="Join your voice channel")
    async def join(self, ctx: commands.Context):
        if not await validate_voice(ctx):
            return

        voice_channel = ctx.author.voice.channel
        voice_client = ctx.voice_client

        if voice_client is None:
            await voice_channel.connect()
        else:
            await voice_client.move_to(voice_channel)

        await safe_send(ctx, f"Joined **{voice_channel.name}**!")

    @commands.hybrid_command(description="Leave the voice channel")
    async def leave(self, ctx: commands.Context):
        if not await validate_voice(ctx, require_bot_connected=True):
            return

        voice_client = ctx.voice_client
        guild_id = ctx.guild.id

        await self.player.clear(guild_id)
        await voice_client.disconnect()
        await safe_send(ctx, f"👋 Leaving **{voice_client.channel.name}**. Stay cool. 😎")
    
    @commands.hybrid_command(description="Play a song or playlist from URL")
    @app_commands.describe(url="The URL of the song or playlist")
    async def play(self, ctx: commands.Context, url: str):
        author_voice = ctx.author.voice
        bot_voice = ctx.voice_client

        if author_voice is None:
            await safe_send(ctx, "You must be in a voice channel first.")
            return
        
        if bot_voice is None:
            await author_voice.channel.connect()
        else:
            if bot_voice.channel != author_voice.channel:
                await safe_send(ctx, "You must be in the same voice channel as The Cooler Bot.")
                return
        
        await ctx.defer()
        await self.player.add_and_maybe_play(ctx, url)
    
    @commands.hybrid_command(description="Show the current queue")
    async def queue(self, ctx: commands.Context):
        await ctx.defer()
        
        guild_id = ctx.guild.id
        current = self.player.get_current(guild_id)
        queue = self.player.get_queue(guild_id)

        embed = queue_embed(current, queue, page=1)
        view = QueuePaginator(ctx, current, queue)
        message = await safe_send(ctx, embed=embed, view=view)
        view.message = message
    
    @commands.hybrid_command(description="Skip the current song")
    async def skip(self, ctx: commands.Context):
        if not await validate_voice(ctx, require_bot_connected=True):
            return
        
        voice_client = ctx.voice_client

        if not voice_client.is_playing():
            await safe_send(ctx, "There's no music playing to skip. 😕")
            return
        
        skipper = ctx.author.display_name
        await self.player.skip(ctx)
        await safe_send(ctx, f"⏭️ **{skipper}** skipped the current song.")
    
    @commands.hybrid_command(description="Pause the current song")
    async def pause(self, ctx: commands.Context):
        if not await validate_voice(ctx, require_bot_connected=True):
            return
        
        voice_client = ctx.voice_client

        if not voice_client.is_playing():
            await safe_send(ctx, "There's no music to pause. 😕")
            return
        
        self.player.pause(ctx)
        await safe_send(ctx, f"⏸️ Music paused by **{ctx.author.display_name}**.")
    
    @commands.hybrid_command(description="Resume the music")
    async def resume(self, ctx: commands.Context):
        if not await validate_voice(ctx, require_bot_connected=True):
            return
        
        voice_client = ctx.voice_client

        if not voice_client.is_paused():
            await safe_send(ctx, "The music is not paused. 🤔")
            return
        
        self.player.resume(ctx)
        await safe_send(ctx, f"▶️ Music resumed by **{ctx.author.display_name}**.")
    
    @commands.hybrid_command(description="Clear the queue")
    async def clear(self, ctx: commands.Context):
        if not await validate_voice(ctx, require_bot_connected=True):
            return
        
        guild_id = ctx.guild.id

        if not self.player.has_next(guild_id):
            await safe_send(ctx, "The queue is already empty.")
            return
        
        await self.player.clear(guild_id)
        await safe_send(ctx, f"🧹 Queue cleared by **{ctx.author.display_name}**.")
    
    @commands.hybrid_command(description="Skip to a specific position in the queue")
    @app_commands.describe(position="Position in the queue to skip to (starting at 1)")
    async def skip_to(self, ctx: commands.Context, position: int):
        if not await validate_voice(ctx, require_bot_connected=True):
            return
        
        await ctx.defer()
        await self.player.skip_to(ctx, position)

    @commands.hybrid_command(description="Shuffles the queue")
    async def shuffle(self, ctx: commands.Context):
        if not await validate_voice(ctx, require_bot_connected=True):
            return
        
        guild_id = ctx.guild.id

        if not self.player.has_next(guild_id):
            await safe_send(ctx, "The queue is empty. Can't be shuffled.")
            return

        await self.player.shuffle(guild_id)
        queue_size = len(self.player.get_queue(guild_id))
        await safe_send(ctx, f"🔀 Shuffled **{queue_size}** songs.")

async def setup(bot):
    await bot.add_cog(Music(bot))
