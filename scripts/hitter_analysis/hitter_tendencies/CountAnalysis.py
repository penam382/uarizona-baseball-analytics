import csv

class CountAnalysis:
    def __init__(self, tendencies):
        self.tendencies = tendencies  # Store the input data
        self.count_data = {}  # This will hold data for all count types
        self.process_data()

    def process_data(self):
        """ Process all tendencies into structured count data """
        if hasattr(self.tendencies, 'tendencies'):
            for count_type, values in self.tendencies.tendencies.items():
                self.count_data[count_type] = []
                for val in values:
                    # Each record is a dictionary for clarity
                    self.count_data[count_type].append({
                        'pitch_type': val[1],
                        'result_type': val[2],
                        'result_outcome': val[3],
                        'pitch_call': val[4],
                        'angle': val[5],
                        'direction': val[6],
                        'distance': val[7],
                        'plate_loc_height': val[8], 
                        'plate_loc_side' : val[9]
                    })
        print(self.count_data)

    def write_data_to_csv(self, filename):
        """ Write the count data to a CSV file """
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write headers
            writer.writerow([
                'Count Type', 'Pitch Type', 'PA_Result_Type', 'PA_Result_Outcome', 'pitch_call',
                'Angle', 'Direction', 'Distance', 'PlateLocHeight', 'PlateLocSide'
            ])
            
            # Iterate over each count type and write data
            for count_type, records in self.count_data.items():
                for record in records:
                    writer.writerow([
                        count_type,
                        record['pitch_type'],
                        record['result_type'],
                        record['result_outcome'],
                        record['pitch_call'],
                        record['angle'],
                        record['direction'],
                        record['distance'],
                        record['plate_loc_height'],
                        record['plate_loc_side']
                    ])
