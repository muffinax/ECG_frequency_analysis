class InputManagerException(Exception):
    def __init__(self, error_id: str, error_description: str) -> None:
        formatted_message: str = f"[{error_id}] {error_description}"
        super().__init__(formatted_message)
        self.error_id: str = error_id
        self.error_description: str = error_description
