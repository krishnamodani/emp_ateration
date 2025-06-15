# recommendation_llm.py

import openai
import os

# Set your OpenAI API Key (ensure the environment variable is set or directly assign here)
openai.api_key = os.getenv("OPENAI_API_KEY")

def rule_based_health_check(avg_scores):
    """
    Returns health status and dictionary of unhealthy survey areas (score < 3.0).
    """
    unhealthy_areas = {k: v for k, v in avg_scores.items() if v < 3.0}
    health_status = "Healthy" if len(unhealthy_areas) <= 3 else "Needs Improvement"
    return health_status, unhealthy_areas

def generate_llm_recommendations(avg_scores, verdict_distribution, total_respondents):
    """
    Uses OpenAI to generate HR recommendations based on average scores and distribution.
    """
    health_status, problem_areas = rule_based_health_check(avg_scores)

    prompt = f"""
You are a senior HR consultant. A company conducted a psychometric survey with {total_respondents} employees.
Based on the following data, provide a summary, key insights, and HR recommendations:

Verdict Distribution:
{verdict_distribution}

Average Satisfaction Scores (1-5 scale):
{avg_scores}

Health Status: {health_status}
Problem Areas (scores < 3.0): {problem_areas}

Please provide:
- A short 3-line health summary
- 3 to 5 improvement areas (titles and bullet tips)
- HR strategies tailored to the problem areas
- Keep the language formal and actionable
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=700
    )

    return health_status, response.choices[0].message["content"]
