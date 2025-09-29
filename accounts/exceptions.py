class StateNotAssignedError(Exception):
    """Raised when attempting to set a default state that is not assigned to the user."""

    def __init__(self, state, user):
        self.state = state
        self.user = user
        super().__init__(f"The state '{state}' is not assigned to the user '{user}'.")