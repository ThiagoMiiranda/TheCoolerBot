class QueueManager:
    def __init__(self):
        # Initializes a queue dict per server (guild)
        self.queues: dict[int, list[dict]] = {}
    
    def add_to_queue(self, guild_id, track):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        self.queues[guild_id].append(track)
    
    def get_queue(self, guild_id):
        return self.queues.get(guild_id, [])
    
    def pop_next(self, guild_id):
        if guild_id in self.queues and self.queues[guild_id]:
            return self.queues[guild_id].pop(0)
        return None
    
    def clear(self, guild_id):
        self.queues[guild_id] = []
    
    def has_next(self, guild_id):
        return bool(self.queues.get(guild_id))