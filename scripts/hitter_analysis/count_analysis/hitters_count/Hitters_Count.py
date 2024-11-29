class Hitters_Count:
    def __init__(self, tendencies):
        # Initialize with the tendencies data
        self.tendencies = tendencies
        # Access the 'tendencies' attribute directly, and then get the 'hitters_count' key
        self.hitters_count_data = self.tendencies.tendencies.get("hitters_count", {})


    def get_hitter_count(self, count_type):
        # Retrieve the hitter count data for a specific count type
        return self.hitters_count_data.get(count_type, [])

    def add_pitch_to_count(self, count_type, pitch_info):
        # Add a new pitch (pitch_type, outcome, location) to the specific count type
        if count_type not in self.hitters_count_data:
            self.hitters_count_data[count_type] = []
        self.hitters_count_data[count_type].append(pitch_info)

    def print_hitter_counts(self):
        # Print all hitter count data (can be customized)
        for count_type, pitches in self.hitters_count_data.items():
            print(f"Count Type: {count_type}")
            for pitch in pitches:
                print(f"  Pitch: {pitch}")


    def __str__(self):
        # Custom string representation for printing the Hitters_Count object
        result = []
        for count_type, pitches in self.hitters_count_data.items():
            result.append(f"Count Type: {count_type}")
            for pitch in pitches:
                result.append(f"  Pitch: {pitch}")
        return "\n".join(result) 

