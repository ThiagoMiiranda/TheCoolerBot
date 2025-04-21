import discord
from discord.ext import commands
import yt_dlp
import asyncio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
    
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
    
    def add_to_queue(self, guild_id, url):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        self.queues[guild_id].append(url)
    
    async def play_next(self, ctx):
        guild_id = ctx.guild.id
        voice_client = ctx.voice_client

        if not self.queues[guild_id]:
            await ctx.send("The playlist is over. 😴")
            return
        
        url = self.queues[guild_id].pop(0)

        ffmpeg_options = {
            'options': '-vn'
        }

        ydl_opts = {
            'format': 'bestaudio',
            'noplaylist': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                source_url = info['url']
                title = info.get("title", "Unknown title")
        except Exception as e:
            await ctx.send(f"❌ Failed to extract audio from URL.\n'''{e}'''")
            return

        try:
            audio_source = await discord.FFmpegOpusAudio.from_probe(source_url, **ffmpeg_options)
            #audio_source = discord.PCMVolumeTransformer(audio_source)
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
        
        
        
        '''async def after_playing():
            try:
                await self.play_next(ctx)
            except Exception as e:
                print(f"Error playing next music: {e}")
            

        def play_and_schedule():
            voice_client.play(audio_source, after=lambda _: self.bot.loop.create_task(after_playing()))
        
        play_and_schedule()'''
        
        await ctx.send(f"▶️ Playing now: {title}")
    
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
        
        guild_id = ctx.guild.id
        self.add_to_queue(guild_id, url)

        if not ctx.voice_client.is_playing():
            await ctx.send("🎵 Let me see what we have here...")
            await self.play_next(ctx)
        else:
            await ctx.send("🎶 Song added to queue!")

async def setup(bot):
    await bot.add_cog(Music(bot))
