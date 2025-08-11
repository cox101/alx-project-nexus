import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Poll

class ResultsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.poll_id = self.scope['url_route']['kwargs']['poll_id']
        self.room_group_name = f'results_{self.poll_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Send initial results
        results = await self.get_poll_results(self.poll_id)
        await self.send(text_data=json.dumps(results))
    
    @database_sync_to_async
    def get_poll_results(self, poll_id):
        poll = Poll.objects.get(id=poll_id)
        return poll.get_results()