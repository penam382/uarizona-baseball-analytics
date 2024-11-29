

class Tendencies:
    def __init__(self):
        self.tendencies = {}

    def add_tendency(self, count_type, count, pitch_type, outcome, location):
        """Adds a new pitch tendency."""
        if count_type not in self.tendencies:
            self.tendencies[count_type, count] = [(pitch_type, outcome, location)]
        else:
            self.tendencies[count_type].append((pitch_type, outcome, location))

    def get_tendencies(self):
        """Returns all recorded tendencies."""
        return self.tendencies

    def clear(self):
        """Clears the recorded tendencies (useful for starting a new analysis)."""
        self.tendencies.clear()


    def __str__(self):
        """Returns a string representation of the tendencies."""
        result = []
        for count_type, pitches in self.tendencies.items():
            result.append(f"Count Type: {count_type}")
            for pitch in pitches:
                pitch_str = f"  Pitch Type: {pitch[0]}, Outcome: {pitch[1]}, Location: {pitch[2]}"
                result.append(pitch_str)
        return "\n".join(result)
