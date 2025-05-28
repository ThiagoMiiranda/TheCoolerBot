import asyncio
import discord
from music.extractor import get_track_info, get_playlist_progressively
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

        # Detects if it is a playlist and use the progressive extraction
        first_track, background_task = await get_playlist_progressively(ctx, url)

        if first_track:
            self.queue_manager.add_to_queue(guild_id, first_track)
            if background_task:
                asyncio.create_task(self._process_playlist(ctx, background_task))
            
            if not voice_client.is_playing():
                await ctx.send(f"🎵 Let me see what we have here...")
                await self.play_next(ctx)
            else:
                await ctx.send(f"Playlist received! First track added: **{first_track['title']}**")
            return

        # If it isn't a playlist, processes as a song as usual
        tracks = await get_track_info(ctx, url)
        if not tracks:
            await ctx.send("❌ Failed to fetch track info.")
            return
        
        for track in tracks:
            self.queue_manager.add_to_queue(guild_id, track)

        if not voice_client.is_playing():
            await ctx.send(f"🎵 Let me see what we have here...")
            await self.play_next(ctx)
        else:
            await ctx.send(f"🎶 Song added to queue: **{tracks[0]['title']}**")

    async def _process_playlist(self, ctx, load_remaining_tracks):
        '''Adds the remaining songs progressively'''
        guild_id = ctx.guild.id
        remaining_tracks = await load_remaining_tracks()

        for track in remaining_tracks:
            self.queue_manager.add_to_queue(guild_id, track)
        
        await ctx.send(f"✅ **{len(remaining_tracks)}** tracks added from the playlist!")
    
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

    async def skip_to(self, ctx, index: int):
        guild_id = ctx.guild.id
        queue = self.queue_manager.get_queue(guild_id)
        voice_client = ctx.voice_client

        if index < 1 or index > len(queue):
            await ctx.send(f"❌ Invalid position. The queue has {len(queue)} songs.")
            return
        
        # Remove the songs before the chosen index
        skipped = queue[:index - 1]
        self.queue_manager.queues[guild_id] = queue[index - 1:]

        await ctx.send(f"⏭️ Skipping **{len(skipped)}** songs.")

        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()
        else:
            await self.play_next(ctx)
