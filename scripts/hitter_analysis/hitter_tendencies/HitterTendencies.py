class HitterTendencies:
    def __init__(self):
        self.tendencies = {}

    def add_tendency(self, count_type, count, pitch_type, result_type, result_outcome, pitch_call, angle, direction, distance, plate_loc_height, plate_loc_side):
        """Adds a new pitch tendency with separated outcome, pitch call, and angle/direction/distance."""
        if count_type not in self.tendencies:
            self.tendencies[count_type] = [(count, pitch_type, result_type, result_outcome, pitch_call, angle, direction, distance, plate_loc_height, plate_loc_side)]
        else:
            self.tendencies[count_type].append((count, pitch_type, result_type, result_outcome, pitch_call, angle, direction, distance, plate_loc_height, plate_loc_side))

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
                pitch_str = f"  Pitch Type: {pitch[1]}, Result: {pitch[2]} {pitch[3]}, Pitch Call: {pitch[4]}, Angle: {pitch[5]}, Direction: {pitch[6]}, Distance: {pitch[7]}, plate_loc_height: {pitch[8]}, plate_loc_side: {pitch[9]}"
                result.append(pitch_str)
        return "\n".join(result)