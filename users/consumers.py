import json
from channels.generic.websocket import AsyncWebsocketConsumer


class UserConsumer(AsyncWebsocketConsumer):
    """
    A consumer that handles WebSocket connections for real-time user updates.
    """
    async def connect(self):
        """
        Called when the websocket is handshaking as part of connection.
        """
        # The group name that all users will join.
        self.group_name = "users_updates"

        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # --- Custom event handlers ---

    async def user_update(self, event):
        """
        Handler for the 'user_update' event sent from the backend.
        This method receives the message from the group and sends it down
        the WebSocket to the client.
        """
        message_data = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message_data))