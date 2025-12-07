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

The suggested action provides the user with a change that should positively impact their wellness score.
Feed the LLM the calculation for the wellness score; ask the LLM to suggest a plan to improve the low score category. 

    "Your wellness score is low because of poor sleep. Try getting more sleep this week by doing xyz"


# Technical Details

## Tech Stack
Backend: Python and FastAPI. Pandas/Numpy for metrics and ML anomaly detection. Runs via uvicorn. [Future: ChatGPT for AI suggestions]

Data: Mock data generated with ChatGPT.

Frontend: React (Vite) with SWR for data fetching.

## Data Layer
Mocked Data in data/mock_health_metrics.csv: 28 days of data. For each day, track calories expended, total sleep duration, resting heart rate, calories consumed, and average HRV.

## Intelligence Layer
### Wellness Score
Create a wellness score based on 4 wellness categories: exercise, sleep, nutrition, and fatigue. Let each factor be equally weighted. Perform unity-based normalization on each metric and then sum each normalized value to compute the wellness score. 

Normalized data = 100 * (X_weekAvg - X_weekMin) / (X_weekMax - X_weekMin)

- X represents a column from the dataset: calories_out,calories_in,total_sleep_mins,rhr,hrv
- Note the normalized metric will be in the range [0,100]

Wellness Score = 0.25*(normalized exercise data) + 0.25*(normalized sleep data) + 0.25*(normalized nutrition data) + 0.25*(normalized fatigue data)

- Note the wellness score will be in the range [0, 100]

### Anomaly Detection and AI Generated Health Suggestion
Run an anomaly detection model on the current week's data vs the past month's data. Extract any anomalies in the data.

Feed the LLM the calculation for the normalized metrics and the wellness score. We can rank each wellness category by how large the normalized metrics are; the smallest normalized metric corresponds to the wellness category that needs most improvement. Tell the LLM that this wellness category could use improvement. Feed the LLM any anomalies in the user's health data. Ask the LLM to suggest a plan to improve the low score category. 

Note: For the hackathon MVP, I won't be hooking the app up to an LLM to generate suggestions. Instead, I'll hard code the suggestions based on the user's health metrics and anomalies.

#### Responsible AI Considerations
All health data should be de-identified before being fed into the LLM.

## Dashboard UI
The MVP will be a dashboard containing components.
1. A component displaying the user's wellness score.
2. A component displaying LLM generated health suggestion based on the user's health metrics and anomalies in the user's health metrics.

## Finer Technical Details, Clarifications, and Working Assumptions for the MVP
- Data schema and units: `calories_out` (kcal), `calories_in` (kcal), `total_sleep_mins` (minutes), `rhr` (bpm), `hrv` (ms). The CSV is 28 sequential days; the most recent row is the current day. Weeks are rolling 7-day windows ending at the latest row; the “past month” baseline uses all 28 days.
- Normalization guardrails: use min-max over the 28-day window. If `weekMax == weekMin`, set the normalized score to 50 for that metric to avoid division by zero and to reflect neutral confidence. Clip extreme outliers to the 1st/99th percentile per metric before normalization to keep scores stable.
- Anomaly detection approach: per metric z-score versus the 28-day baseline mean/std. Flag anomalies at |z| >= 1.5 with at least 14 days of history. Report anomalies as `{metric, value, baseline_mean, z_score, direction}` so they can be rendered and fed to the LLM with context. I'll use existing ML python libraries to implement anomaly detection.
- LLM constraints: keep guidance non-medical and action-oriented (sleep, nutrition, activity habits). Prompt with: current week normalized metrics, wellness score, ranked weakest metric, and any anomalies (value and direction). If no networked LLM is available, fall back to a deterministic template recommendation.
- API/UI contract (single-user demo): backend returns JSON like `{week_range: {start, end}, wellness_score, normalized_metrics: {exercise, sleep, nutrition, fatigue}, anomalies: [...], suggestion: {text, caveats}}`. React renders wellness score and suggestion; anomalies can be shown inline or used solely for the LLM prompt.
- [Optional/Future Enhancement] Testing baseline: add unit tests for (1) normalization with zero-variance and outlier clipping, (2) wellness score aggregation, and (3) anomaly detection thresholds. Validate with the provided 28-day fixture to ensure deterministic outputs for the demo.

# Future Enhancements for the future
- Allow the user to see the dashboard content from previous weeks
- Allow the user to compare content from previous weeks
- Allow the user to upload their progress pictures, which will be associated with the user's data and stats from that timeframe.
- Allow the user to drill down into the raw data to analyze how specific nutrition, sleep, and exercise data affects their well-being stats over time.
- In addition to the wellness score, generate an AI summary of how that week went and how your progress was trending during that time period.
- Feed wellness data (current activity data / workout plan, current diet plan, weight, recovery needs based on resting heart rate and HRV) through a LLM to generate a workout and diet plan for the week given the user's goals (weight loss, strength, endurance, recovery, etc).
