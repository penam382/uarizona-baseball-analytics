class HitterTendencies:
    def __init__(self):
        self.tendencies = {}

    def add_tendency(self, count_type, count, pitch_type, result_type, result_outcome, pitch_call, angle, direction, distance, location):
        """Adds a new pitch tendency with separated outcome, pitch call, and angle/direction/distance."""
        if count_type not in self.tendencies:
            self.tendencies[count_type] = [(count, pitch_type, result_type, result_outcome, pitch_call, angle, direction, distance, location)]
        else:
            self.tendencies[count_type].append((count, pitch_type, result_type, result_outcome, pitch_call, angle, direction, distance, location))

    def get_tendencies(self):
        """Returns all recorded tendencies."""
        return self.tendencies

    def clear(self):
        """Clears the recorded tendencies."""
        self.tendencies.clear()

    def __str__(self):
        """Returns a string representation of the tendencies."""
        result = []
        for count_type, pitches in self.tendencies.items():
            result.append(f"Count Type: {count_type}")
            for pitch in pitches:
                pitch_str = f"  Pitch Type: {pitch[1]}, Result: {pitch[2]} {pitch[3]}, Pitch Call: {pitch[4]}, Angle: {pitch[5]}, Direction: {pitch[6]}, Distance: {pitch[7]}, Location: {pitch[8]}"
                result.append(pitch_str)
        return "\n".join(result)