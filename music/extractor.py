import yt_dlp
import asyncio
from utils.message import safe_send

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': False,
    'quiet': True,
    'extract_flat': 'in_playlist',
    'default_search': 'ytsearch',
    'skip_download': True
}

def _extract_info_sync(url: str):
    '''Fetch metadata and audio stream URL from a YouTube URL without downloading.'''
    with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ytdl:
        return ytdl.extract_info(url, download=False)

async def get_playlist_progressively(ctx, url: str):
    '''Returns the playlist's first song and load the remaining in background.'''
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, _extract_info_sync, url)

    # Isn't a playlist
    if 'entries' not in data:
        return None, None
    
    flat_entries = data['entries']

    # Empty playlist
    if not flat_entries:
        return None, None
    
    first_track = None
    while flat_entries and first_track is None:
        first_entry = flat_entries.pop(0)
        try:
            detailed_data = await loop.run_in_executor(None, _extract_info_sync, first_entry['url'])
            first_track = {
                'title': detailed_data.get('title'),
                'webpage_url': detailed_data.get('webpage_url'),
                'source_url': detailed_data.get('url'),
                'requested_by': ctx.author.display_name
            }
        except Exception as e:
            print(f"Error loading the first song from the playlist: {e}")
            await safe_send(ctx, "A song from the start of the playlist was ignored (probably private or removed)")

    async def load_remaining_tracks():
        '''Load remaining songs in background.'''
        tracks = []
        for entry in flat_entries:
            if not entry:
                continue
            try:
                detailed_data = await loop.run_in_executor(None, _extract_info_sync, entry['url'])

                track = {
                    'title': detailed_data.get('title'),
                    'webpage_url': detailed_data.get('webpage_url'),
                    'source_url': detailed_data.get('url'),
                    'requested_by': ctx.author.display_name
                }

                tracks.append(track)

                # Visual feedback of loading process
                if len(tracks) % 5 == 0:
                    await safe_send(ctx, f"🎶 {len(tracks)} tracks added so far...")
            except Exception as e:
                print(f"Error loading a song from the playlist: {e}")
                await safe_send(ctx, "A song from the playlist was ignored (probably private or removed)")
                continue
        return tracks
    
    return first_track, load_remaining_tracks

async def get_track_info(ctx, url: str):
    # Executes yt_dlp out of the main loop, in a separated thread, to avoid hanging the bot.
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, _extract_info_sync, url)

    # If it's a playlist
    if 'entries' in data:
        flat_entries = data['entries']
        tracks = []
        
        for flat_entry in flat_entries:
            # Some entry might be None
            if not flat_entry:
                continue

            detailed_data = await loop.run_in_executor(None, _extract_info_sync, flat_entry['url'])

            track = {
                'title': detailed_data.get('title'),
                'webpage_url': detailed_data.get('webpage_url'),
                'source_url': detailed_data.get('url'),
                'requested_by': ctx.author.display_name
            }
            tracks.append(track)
        return tracks
    
    # If it's only a song
    track = {
        'title': data.get('title'),
        'webpage_url': data.get('webpage_url'),
        'source_url': data.get('url'),
        'requested_by': ctx.author.display_name
    }
    return [track]
