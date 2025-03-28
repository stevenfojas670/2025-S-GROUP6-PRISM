from channels.generic.websocket import AsyncWebsocketConsumer
import json


class MyConsumer(AsyncWebsocketConsumer):
    """MyConsumer is an asynchronous WebSocket consumer that handles WebSocket
    connections.

    Methods:
        Handles the WebSocket connection establishment. Accepts the connection
        and sends a message indicating that the WebSocket is connected.
        Handles incoming messages from the WebSocket. Sends back a response
        containing the received message.
        Handles the WebSocket disconnection. Logs the disconnection with the
        provided close code.
    Attributes:
        None
    """

    async def connect(self):
        """Handles the WebSocket connection event.

        This method is called when a WebSocket client attempts to establish a connection.
        It accepts the connection and sends an initial message to the client indicating
        that the WebSocket connection has been successfully established.

        Sends:
            A JSON-formatted message with a "message" key and the value "WebSocket connected".
        """
        await self.accept()
        await self.send(text_data=json.dumps({"message": "WebSocket connected"}))

    async def receive(self, text_data):
        """Handles the receipt of a WebSocket message.

        This asynchronous method is triggered when a message is received
        from the WebSocket. It processes the incoming `text_data` and sends
        a JSON response back to the client with the received message.

        Args:
            text_data (str): The text data received from the WebSocket.

        Returns:
            None
        """
        await self.send(text_data=json.dumps({"message": f"You sent: {text_data}"}))

    async def disconnect(self, close_code):
        """Handles the WebSocket disconnection event.

        This method is called when the WebSocket connection is closed.
        It logs the disconnection event along with the provided close code.

        Args:
            close_code (int): The close code indicating the reason for disconnection.
        """
        print(f"WebSocket disconnected: {close_code}")
