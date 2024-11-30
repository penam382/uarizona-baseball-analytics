class Tendencies:
    def __init__(self):
        self.tendencies = {}

    def add_tendency(self, count_type, count, pitch_type, result_type, result_outcome, angle, direction, distance, location):
        """Adds a new pitch tendency with separated outcome and angle/direction/distance."""
        if count_type not in self.tendencies:
            self.tendencies[count_type] = [(count, pitch_type, result_type, result_outcome, angle, direction, distance, location)]
        else:
            self.tendencies[count_type].append((count, pitch_type, result_type, result_outcome, angle, direction, distance, location))

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
                pitch_str = f"  Pitch Type: {pitch[1]}, Result: {pitch[2]} {pitch[3]}, Angle: {pitch[4]}, Direction: {pitch[5]}, Distance: {pitch[6]}, Location: {pitch[7]}"
                result.append(pitch_str)
        return "\n".join(result)
