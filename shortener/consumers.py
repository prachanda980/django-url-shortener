import json
from channels.generic.websocket import AsyncWebsocketConsumer

class URLConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time URL updates.
    All users join the 'url_updates' group to receive broadcasts.
    """
    async def connect(self):
        self.group_name = 'url_updates'

        # Join the global group for updates
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def url_update(self, event):
        """
        Handler for messages sent to the 'url_updates' group.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['data']))
