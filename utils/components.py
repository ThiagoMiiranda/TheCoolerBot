import discord

class MusicControlView(discord.ui.View):
    def __init__(self, player, ctx):
        super().__init__(timeout=None)
        self.player = player
        self.ctx = ctx
    
    @discord.ui.button(label="⏯️ Play/Pause", style=discord.ButtonStyle.blurple)
    async def play_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ You must be in a voice channel.", ephemeral=True)
            return
        
        voice_client = interaction.guild.voice_client
        if not voice_client:
            await interaction.response.send_message("❌ I'm not in a voice channel.", ephemeral=True)
            return
        
        if voice_client.is_playing():
            self.player.pause(self.ctx)
            await interaction.response.send_message("⏸️ Paused.", ephemeral=True)
        elif voice_client.is_paused():
            self.player.resume(self.ctx)
            await interaction.response.send_message("▶️ Resumed.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Nothing to play/pause.", ephemeral=True)

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.green)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.player.skip(self.ctx)
        await interaction.response.send_message("⏭️ Skipped.", ephemeral=True)
    
    @discord.ui.button(label="🛑 Stop", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.player.clear(interaction.guild.id)

        voice_client = interaction.guild.voice_client
        if voice_client:
            await voice_client.disconnect()
        
        await interaction.response.send_message(f"👋 Leaving **{voice_client.channel.name}**. Stay cool. 😎", ephemeral=True)
