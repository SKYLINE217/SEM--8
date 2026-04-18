# CS 102 Requirement: StateMachine implementation
class StateMachine:
    def __init__(self):
        self.states = ["IDLE", "HEATING", "COMPRESSION", "CURING", "EJECTION"]
        self.current_state = "IDLE"
        self.transitions = {
            "IDLE": ["HEATING"],
            "HEATING": ["COMPRESSION"],
            "COMPRESSION": ["CURING"],
            "CURING": ["EJECTION"],
            "EJECTION": ["IDLE"]
        }

    def transition(self, next_state):
        if next_state in self.transitions[self.current_state]:
            self.current_state = next_state
            return True
        return False

    def get_state(self):
        return self.current_state
