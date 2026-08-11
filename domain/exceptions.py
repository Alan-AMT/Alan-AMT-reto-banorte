class DomainException(Exception):
    """Base exception for domain errors."""
    pass


class ChatSessionNotFoundError(DomainException):
    """Raised when a requested chat session is not found."""
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Chat session '{session_id}' was not found.")
