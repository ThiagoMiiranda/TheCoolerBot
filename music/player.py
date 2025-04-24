import asyncio
import discord
from music.extractor import get_track_info
from music.queue_manager import QueueManager

class MusicPlayer:
    def __init__(self, bot):
        # Manages music playback, control and status on a per-server basis.
        self.bot = bot
        self.queue_manager = QueueManager()
        self.current = {}
    
    async def play_next(self, ctx):
        guild_id = ctx.guild.id
        voice_client = ctx.voice_client

        track = self.queue_manager.pop_next(guild_id)
        if not track:
            await ctx.send("📭 The playlist is over. 😴")
            self.current[guild_id] = None
            return
        
        self.current[guild_id] = track

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        try:
            audio_source = await discord.FFmpegOpusAudio.from_probe(track['source_url'], **ffmpeg_options)
        except Exception as e:
            await ctx.send(f"❌ Failed to play track.\n'''{e}'''")
            return
        
        def after_playing(error):
            if error:
                print(f"Playback error: {error}")
            fut = asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
            try:
                fut.result()
            except Exception as e:
                print(f"Error playing next music: {e}")
        
        if not voice_client:
            await ctx.send("The Cooler Bot isn't in a voice channel.")
            return
        
        voice_client.play(audio_source, after=after_playing)
        await ctx.send(f"▶️ Now playing: **{track['title']}**")
    
    async def add_and_maybe_play(self, ctx, url: str):
        guild_id = ctx.guild.id
        voice_client = ctx.voice_client

        track = await get_track_info(ctx, url)
        if not track:
            await ctx.send("❌ Failed to fetch track info.")
            return
        self.queue_manager.add_to_queue(guild_id, track)

        if not voice_client.is_playing():
            await ctx.send("🎵 Let me see what we have here...")
            await self.play_next(ctx)
        else:
            await ctx.send(f"🎶 Song added to queue: **{track['title']}**")
    
    async def skip(self, ctx):
        voice_client = ctx.voice_client
        voice_client.stop()
    
    async def clear(self, guild_id):
        self.queue_manager.clear(guild_id)
        self.current[guild_id] = None
    
    def pause(self, ctx):
        voice_client = ctx.voice_client
        voice_client.pause()

    def resume(self, ctx):
        voice_client = ctx.voice_client
        voice_client.resume()
    
    def get_current(self, guild_id):
        return self.current.get(guild_id)
    
    def get_queue(self, guild_id):
        return self.queue_manager.get_queue(guild_id)
    
    def has_next(self, guild_id):
        return self.queue_manager.has_next(guild_id)
