import discord

async def safe_send(ctx, content=None, **kwargs):
    # Sends a message safely, falls back to followup if interaction has been responded.
    try:
        return await ctx.send(content=content, **kwargs)
    except (AttributeError, discord.InteractionResponded):
        return await ctx.followup.send(content=content, **kwargs)
    except discord.HTTPException as e:
        print(f"Failed to send message: {e}")
