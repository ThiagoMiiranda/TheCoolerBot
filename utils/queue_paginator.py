import discord
import math
from utils.embeds import queue_embed

class QueuePaginator(discord.ui.View):
    def __init__(self, ctx, current, queue, player):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.queue = queue
        self.current = current
        
        self.player = player
        self.guild_id = ctx.guild.id

        self.items_per_page = 10
        self.total_pages = max(1, math.ceil(len(queue) / self.items_per_page))
        self.page = 1

        self.update_buttons()
    
    def update_buttons(self):
        self.prev_button.disabled = self.page <= 1
        self.next_button.disabled = self.page >= self.total_pages
    
    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.blurple)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ You're not allowed to control this queue.", ephemeral=True)
            return
        
        self.page -= 1
        self.update_buttons()

        embed = queue_embed(self.current, self.queue, self.page, self.items_per_page)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🔀 Shuffle", style=discord.ButtonStyle.green)
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ You're not allowed to control this queue.")
            return
        
        if len(self.queue) < 2:
            await interaction.response.send_message("The queue needs at least 2 songs to shuffle.", ephemeral=True)
            return
        
        await self.player.shuffle(self.guild_id)
        self.queue = self.player.get_queue(self.guild_id)

        self.total_pages = max(1, math.ceil(len(self.queue) / self.items_per_page))
        self.page = min(self.page, self.total_pages)
        self.update_buttons()

        embed = queue_embed(self.current, self.queue, self.page, self.items_per_page)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="➡️", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ You're not allowed to control this queue.", ephemeral=True)
            return
        
        self.page += 1
        self.update_buttons()

        embed = queue_embed(self.current, self.queue, self.page, self.items_per_page)
        await interaction.response.edit_message(embed=embed, view=self)
