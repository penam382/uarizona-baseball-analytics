class Hitter:
    def __init__(self, plate_appearance_id, batter_name):
        self.plate_appearance_id = plate_appearance_id
        self.batter_name = batter_name
        self.outcome = {} # {hit_result : (tuple)}
        self.strikes = 0
        self.balls = 0
        self.pitches = []
        self.location_of_pitch = []
        self.pitch_type = {} # {pitchNum : type of pitch}
        self.tendencies = {}  # {count_type: [(pitch_type, outcome)]}
        self.strikeouts = 0
        self.walks = 0

    def type_of_count(self):
        """
        Determines the type of count based on the current strikes and balls.
        """
        if self.balls == 0 and self.strikes == 0:
            return "0-0 Count"
        if self.balls == 3 and self.strikes == 2:
            return "Full Count"
        if (self.balls == 3 and self.strikes <= 1) or (self.balls == 2 and self.strikes == 1) or (self.balls == 2 and self.strikes == 0):
            return "Hitter's Count"
        if (self.strikes >= 2) or (self.balls <= 1 and self.strikes == 1):
            return "Pitcher's Count"
        return "Neutral Count"


    def count(self):
        """
        Returns the current ball-strike count as a formatted string.
        """
        return f"{self.balls} - {self.strikes}"
        
    def total_pitches(self):
        """
        Returns the total number of pitches in the plate appearance.
        """
        return len(self.pitches)
    
    def outcome_of_PA(self, play_result_and_hit_type, angle_direction, korbb):

        play_result, hit_type = play_result_and_hit_type

        if play_result != 'Undefined' and hit_type != 'Undefined':
            self.outcome["PA_result"] = play_result_and_hit_type
            self.outcome["angle_direction"] = angle_direction
        if korbb != 'Undefined':
            self.outcome["PA_result"] = korbb
            self.strikeouts += 1
            self.walks += 1
            
            

    def process_pitch(self, location, pitch_type, pitch_of_pa, balls, strikes):
        self.balls = balls
        self.strikes = strikes
        self.location_of_pitch.append(location)
        self.pitch_type[pitch_of_pa] = pitch_type
        self.pitches.append({
            'pitch_of_pa': pitch_of_pa,
            'location': location,
            'pitch_type': pitch_type,
            'count': self.count(),
        })


    def log_tendency(self, count_type, pitch_type, location):
        # for specific pitch: log what happened and what pitch they got.

        if count_type not in self.tendencies:
            self.tendencies[count_type] = [(pitch_type, self.outcome, location)]
        else:
            self.tendencies[count_type].append([(pitch_type, self.outcome, location)])

    def get_strikeout_walk_total(self):
        return (f"Total Strikouts: {self.strikeouts}, Total Walks: {self.walks}")


    
    def to_tabular_data(self):
        """
        Returns a list of dictionaries, where each dictionary represents a pitch.
        """
        tabular_data = []
        for pitch_num, pitch_type in self.pitch_type.items():
            tabular_data.append({
                "Plate Appearance ID": self.plate_appearance_id,
                "Batter Name": self.batter_name,
                "Pitch Number": pitch_num,
                "Pitch Type": pitch_type,
                "Balls": self.balls,
                "Strikes": self.strikes,
                "PlateLocHeight": self.location_of_pitch[pitch_num - 1][0],
                "PlateLocSide": self.location_of_pitch[pitch_num - 1][1],
                "Outcome": self.outcome[-1] if self.outcome else None,
                "Count Type": self.type_of_count()
                
            })
        return tabular_data



    def __repr__(self):
        return (f"Hitter({self.plate_appearance_id}, {self.batter_name}, Strikes: {self.strikes}, "
                f"Balls: {self.balls}, Total Pitches: {self.total_pitches()}, "
                f"Outcome: {self.outcome})")

