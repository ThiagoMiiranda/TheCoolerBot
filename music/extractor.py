import yt_dlp
import asyncio

async def get_track_info(ctx, url):
    '''Fetch metadata and audio stream URL from a YouTube URL without downloading.'''
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
                'source_url': info['url'],
                'requested_by': ctx.author.display_name
            }
    
    # Executes yt_dlp out of the main loop, in a separated thread, to avoid hanging the bot.
    return await loop.run_in_executor(None, run_ydl)