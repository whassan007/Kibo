from .microsoft import MicrosoftGraphProvider
from .google import GoogleCalendarProvider

def get_provider(name: str):
    if name == "microsoft":
        return MicrosoftGraphProvider()
    elif name == "google":
        return GoogleCalendarProvider()
    else:
        raise ValueError(f"Unsupported provider: {name}")
