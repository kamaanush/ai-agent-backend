class MCPManager:
    def __init__(self):
        self.tools = [
            {"name": "gmail_agent", "description": "Access Gmail to read/send emails"},
            {"name": "calendar_agent", "description": "Access Google Calendar events"},
            {"name": "shopping_agent", "description": "Search and order products online"},
        ]

    def list_tools(self):
        return self.tools
