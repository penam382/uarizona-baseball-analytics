import csv

class CountAnalysis:
    def __init__(self, tendencies):
        self.tendencies = tendencies  # Store the input data
        self.count_data = {}  # This will hold data for all count types
        self.process_data()

    def process_data(self):
        # Ensure tendencies attribute exists
        if hasattr(self.tendencies, 'tendencies'):
            # Loop through each count type in tendencies
            for key, value in self.tendencies.tendencies.items():
                # Initialize the lists for the count type
                self.count_data[key] = {
                    'pitch_types': [],
                    'outcomes': [],
                    'angles': [],
                    'directions': [],
                    'distances': [],
                    'locations': [],
                    'pitch_counter': {}
                }
                # Process the data for this specific count
                self.process_count_data(key, value)

    def process_count_data(self, count_type, value):
        """ Process data for any count type dynamically """
        for val in value:
            # Append pitch types, outcomes, and locations to the appropriate lists
            self.count_data[count_type]['pitch_types'].append(val[1])

            # Extract result_type and result_outcome (already separated in your data)
            result_type = val[2]
            result_outcome = val[3]
            self.count_data[count_type]['outcomes'].append((result_type, result_outcome))  # Storing as tuple
            self.count_data[count_type]['angles'].append(val[4])
            self.count_data[count_type]['directions'].append(val[5])
            self.count_data[count_type]['distances'].append(val[6])
            self.count_data[count_type]['locations'].append(val[7])

        # After adding data, calculate the pitch counts
        self.calculate_pitch_counts(count_type)

    def calculate_pitch_counts(self, count_type):
        """ Calculate pitch type counts for any given count type """
        pitch_types = self.count_data[count_type]['pitch_types']
        pitch_counter = self.count_data[count_type]['pitch_counter']

        for pitch in pitch_types:
            if pitch not in pitch_counter:
                pitch_counter[pitch] = 1
            else:
                pitch_counter[pitch] += 1

    def get_count_data(self, count_type):
        """ Retrieve data for a specific count type """
        return self.count_data.get(count_type, {})

    def get_all_counts(self):
        """ Retrieve data for all count types """
        return self.count_data

    def write_data_to_csv(self, filename):
        """ Write the count data to a CSV file """
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write headers with additional columns for angle, direction, and distance
            writer.writerow([
                'Count Type', 'Pitch Type', 'PA_Result_Type', 'PA_Result_Outcome', 
                'Angle', 'Direction', 'Distance', 'Location'
            ])
            
            # Iterate over each count type and write data
            for count_type, count_info in self.count_data.items():
                pitch_types = count_info['pitch_types']
                outcomes = count_info['outcomes']
                angles = count_info['angles']
                directions = count_info['directions']
                distances = count_info['distances']
                locations = count_info['locations']
                
                max_len = max(len(pitch_types), len(outcomes), len(angles), len(directions), len(distances), len(locations))
                
                for i in range(max_len):
                    # Extract PA_Result_Type and PA_Result_Outcome from the tuple (result_type, result_outcome)
                    result_type = outcomes[i][0] if i < len(outcomes) else ''
                    result_outcome = outcomes[i][1] if i < len(outcomes) else ''
                    
                    # Write each row for this count type
                    writer.writerow([
                        count_type,
                        pitch_types[i] if i < len(pitch_types) else '',
                        result_type,  # PA_Result_Type
                        result_outcome,  # PA_Result_Outcome
                        angles[i] if i < len(angles) else '',
                        directions[i] if i < len(directions) else '',
                        distances[i] if i < len(distances) else '',
                        locations[i] if i < len(locations) else ''
                    ])
