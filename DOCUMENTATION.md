# Background and Problem Statement
Health-conscious individuals are often drowning in data from a
multitude of disconnected sources—a wearable tracking sleep, an app for logging nutrition, a
smart scale for weight, and a blood pressure monitor. This data fragmentation makes it nearly
impossible to see the bigger picture and understand the complex interplay between diet,
exercise, sleep, and overall well-being.

There needs to be a way to aggregate health data to provide a single view of a user's wellness. This data needs to be digested in actionable insights.

# Research
### Health Data 
What data can we track? (non-exhuastive list)
- Steps
- Activity Data
    - Calories expended
        - Resting calories
        - Active calories
    - Duration
    - Average Heart Rate
    - Max Heart Rate
    - Activity Type and Activity Specific Data
        - Running
            - Cadence, Power, Pace
        - Walking
        - Cycling
        - Swimming
        - Weight Training
- Sleep Data
    - Sleep Heart Rate
    - Heart Rate Variability (HRV)
    - Total Duration
        - Duration in sleep stages
- Biological Data
    - Age
    - Weight
    - Height
    - Resting Heart Rate
    - Blood Pressure
- Nutrition Data
    - Macros
    - Calories consumed
    - Hydration
    - Supplement intake
- Miscellaneous Data
    - Progress pictures

Which metrics have a causal relationship?
- [Decreased Heart Rate Variability Is Associated with Increased Fatigue](https://pmc.ncbi.nlm.nih.gov/articles/PMC12452775/)
- [Diet, Sleep and Exercise: The Keystones of Healthy Lifestyle](https://pmc.ncbi.nlm.nih.gov/articles/PMC9794932/)

# Scope
Due to the time constraints of this hackathon, I'll simplify the solution. Let's encapsulate activity data with calories expended, sleep data with total sleep duration, biological data with resting heart rate, and nutrition data with calories consumed. 

Additionally, I'll use the article cited above to say that heart rate variability (HRV) is a proxy for fatigue.

# Proposed Solution + MVP

Create a dashboard that aggregates the user's health data and packages it up into a digestible weekly summary. The dahsboard will contain components for a wellness score (based on aggregated and normalized data) and notable trends (based on ML anomaly detection) and insight suggestion (prompt-based LLM). 

The wellness score gives the user a high-level overview of their personal health for that week.

    Wellness Score: 67/100

The notable trends gives the user a deeper insight into anomalies that could be affecting their overall well-being.

    "Your resting heart rate was higher than normal this week, indicating your body's need for rest and recovery"
    "Your calorie consumption was lower than normal this week, which meant you had less energy based on your calorie expenditure"
    "You got less sleep this week than normal, causing you to have less energy"
    "You were more active than normal this week, causing you to feel more fatigued based on your HRV"

The suggested action provides the user with a change that should positively impact their wellness score.
Feed the LLM the calculation for the wellness score; ask the LLM to suggest a plan to improve the low score category. 

    "Your wellness score is low because of poor sleep. Try getting more sleep this week by doing xyz"


# Technical Stack and Technical Details

## Data Layer
Mocked Data: 28 days of data. For each day, track calories expended, total sleep duration, resting heart rate, calories consumed, and average HRV.

## Intelligence Layer
### Wellness Score
Create a wellness score based on exercise, sleep, nutrition, and fatigue. Let each factor be equally weighted. Perform unity-based normalization on each metric and then sum each normalized value to compute the wellness score. 

Normalized data = 100 * (X_weekAvg - X_weekMin) / (X_weekMax - X_weekMin)

- Note the normalized metric will be in the range [0,100]

Wellness Score = 0.25*(normalized exercise data) + 0.25*(normalized sleep data) + 0.25*(normalized nutrition data) + 0.25*(normalized fatigue data)

- Note the wellness score will be in the range [0, 100]

### Anomaly Detection and AI Generated Health Suggestion
Run an anomaly detection model on the current week's data vs the past month's data. Extract any anomalies in the data.

Feed the LLM the calculation for the normalized metrics and the wellness score; we can rank each category by how much room for improvement there is based on the normalized metrics. Feed the LLM any anomalies in the user's health data.Ask the LLM to suggest a plan to improve the low score category. 

## Dashboard API
Python backend -> JSON -> React

## Dashboard UI

# Future Enhancements
- Allow the user to see the dashboard content from previous weeks
- Allow the user to compare content from previous weeks
- Allow the user to upload their progress pictures, which will be associated with the user's data and stats from that timeframe.
- Allow the user to drill down into the raw data to analyze how specific nutrition, sleep, and exercise data affects their well-being stats over time.
- In addition to the wellness score, generate an AI summary of how that week went and how your progress was trending during that time period.
- Feed wellness data (current activity data / workout plan, current diet plan, weight, recovery needs based on resting heart rate and HRV) through a LLM to generate a workout and diet plan for the week given the user's goals (weight loss, strength, endurance, recovery, etc).