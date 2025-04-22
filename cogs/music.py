import discord
from discord.ext import commands
import yt_dlp
import asyncio

class Music(commands.Cog):
    '''Cog that handles music playback and queue management.'''
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.current = {}
    
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
    
    def add_to_queue(self, guild_id, track):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        self.queues[guild_id].append(track)
    
    async def get_track_info(self, url):
        '''Fetche metadata and audio stream URL from a YouTube URL without downloading.'''
        ydl_opts = {
            'format': 'bestaudio',
            'noplaylist': True
        }

        loop = asyncio.get_event_loop()

        def run_ydl():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'url': url,
                    'title': info.get('title', 'Unknown title'),
                    'source_url': info['url']
                }
        
        # Executes yt_dlp out of the main loop, in a separated thread, to avoid hanging the bot.
        return await loop.run_in_executor(None, run_ydl)
    
    async def play_next(self, ctx):
        '''Plays the next song from queue and schedule the upcoming one.'''
        guild_id = ctx.guild.id
        voice_client = ctx.voice_client

        if not self.queues[guild_id]:
            await ctx.send("The playlist is over. 😴")
            return
        
        track = self.queues[guild_id].pop(0)
        self.current[guild_id] = track
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        try:
            audio_source = await discord.FFmpegOpusAudio.from_probe(track['source_url'], **ffmpeg_options)
        except Exception as e:
            await ctx.send(f"❌ Failed to create audio source.\n'''{e}'''")
            return

        def after_playing(error):
            if error:
                print(f"Playback error: {error}")
            fut = asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
            try:
                fut.result()
            except Exception as e:
                print(f"Error playing next music: {e}")
        
        voice_client.play(audio_source, after=after_playing)
        await ctx.send(f"▶️ Now playing: **{track['title']}**")
    
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
        
        track = await self.get_track_info(url)
        guild_id = ctx.guild.id
        self.add_to_queue(guild_id, track)

        if not ctx.voice_client.is_playing():
            await ctx.send("🎵 Let me see what we have here...")
            await self.play_next(ctx)
        else:
            await ctx.send(f"🎶 Song added to queue: **{track['title']}**")
    
    @commands.command(name="queue")
    async def show_queue(self, ctx):
        guild_id = ctx.guild.id

        now_playing = self.current.get(guild_id)
        upcoming = self.queues.get(guild_id, [])

        if not now_playing and not upcoming:
            await ctx.send("📭 The queue is currently empty.")
            return
        
        message = ""

        if now_playing:
            message += f"🎧 **Now playing:** {now_playing['title']}\n\n"
        
        if upcoming:
            message += f"🎶 **Upcoming songs:**\n"
            for i, track in enumerate(upcoming, start=1):
                message += f"{i}. {track['title']}\n"
        
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(Music(bot))
