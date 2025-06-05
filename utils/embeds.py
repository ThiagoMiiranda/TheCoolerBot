import discord
import math

def now_playing_embed(track: dict) -> discord.Embed:
    embed = discord.Embed(
        title="🎶 Now Playing",
        description=f"[{track['title']}]({track['webpage_url']})",
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 Requested by", value=track.get('requested_by', 'Unknown'), inline=True)
    embed.set_thumbnail(url=track.get('thumbnail'))

    return embed

def queue_embed(current: dict, queue: list, page: int = 1, items_per_page: int = 10) -> discord.Embed:
    total_pages = max(1, math.ceil(len(queue) / items_per_page))
    
    embed = discord.Embed(
        title=f"🎧 Songs Queue - Page {page}/{total_pages}",
        color=discord.Color.purple()
    )

    if current:
        embed.add_field(
            name="🎶 Now Playing",
            value=f"[{current['title']}]({current['webpage_url']}) (Requested by {current.get('requested_by', 'Unknown')})",
            inline=False
        )
    
    if queue:
        start = (page - 1) * items_per_page
        end = start + items_per_page
        queue_page = queue[start:end]

        # desc = ""
        for i, track in enumerate(queue_page, start=start + 1):
            embed.add_field(
                name=f"{i}. {track['title'][:250]}",
                value=f"[Link]({track['webpage_url']}) • Requested by {track.get('requested_by', 'Unknown')}",
                inline=False
            )
            
            
            # desc += f"**{i}.** [{track['title']}]({track['webpage_url']}) (by {track.get('requested_by', 'Unknown')})\n"
        
        # embed.add_field(name="Upcoming", value=desc, inline=False)
    else:
        embed.add_field(name="Upcoming", value="The queue is empty.", inline=False)
    
    embed.set_footer(text="Use the buttons below to navigate pages.")
    return embed
