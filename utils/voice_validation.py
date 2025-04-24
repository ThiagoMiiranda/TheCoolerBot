async def validate_voice(ctx, require_bot_connected=False):
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