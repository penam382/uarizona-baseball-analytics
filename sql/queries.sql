-- SQL queries for analysis


-- caulfield_pitch_count
SELECT TaggedPitchType, COUNT(*) AS Total
FROM pitches
WHERE Batter = 'Caulfield, Garen'
GROUP BY TaggedPitchType
ORDER BY Total DESC;

-- distinct_batters
SELECT DISTINCT Batter
FROM pitches;

-- pitch_type_distribution
SELECT TaggedPitchType, AVG(RelSpeed) AS AvgSpeed
FROM pitches
GROUP BY TaggedPitchType;
