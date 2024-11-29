class Hitter:
    def __init__(self, plate_appearance_id, batter_name):
        self.plate_appearance_id = plate_appearance_id
        self.batter_name = batter_name
        self.outcome = [] # Stores results of the plate appearance
        self.strikes = 0
        self.balls = 0
        self.location_of_pitch = []
        self.pitch_type = {} # {pitchNum : type of pitch}
        self.tendencies = {}  # {count_type: [(pitch_type, outcome)]}

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
    
    def outcome_of_PA(self, play_result, hit_type):
        if play_result != 'Undefined' and hit_type != 'Undefined':
            result_and_hit_type = (play_result, hit_type)
            self.outcome.append(result_and_hit_type)
            

    def process_pitch(self, location, pitch_type, pitch_of_PA):
        # location = (PlateLocHeight, PlateLocSide) 
        self.location_of_pitch.append(location)
        self.pitch_type[pitch_of_PA] = pitch_type


    def log_tendency(self, count_type, pitch_type, outcome, location):
        # for specific pitch: log what happened and what pitch they got.

        if count_type not in self.tendencies:
            self.tendencies[count_type] = [(pitch_type, outcome, location)]


    def __repr__(self):
        return (f"Hitter({self.plate_appearance_id}, {self.batter_name}, Strikes: {self.strike_count}, "
                f"Balls: {self.ball_count}, InPlay: {self.in_play}, HitByPitch: {self.hit_by_pitch}, "
                f"Total Pitches: {self.total_pitches})")
