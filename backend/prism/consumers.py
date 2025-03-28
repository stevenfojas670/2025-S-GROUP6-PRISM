from channels.generic.websocket import AsyncWebsocketConsumer
import json


class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({"message": "WebSocket connected"}))

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({"message": f"You sent: {text_data}"}))

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected: {close_code}")
