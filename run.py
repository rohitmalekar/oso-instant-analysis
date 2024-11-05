import pandas as pd
import streamlit as st
import plotly.express as px  # Import Plotly Express
from datetime import datetime, timezone 

# Read the CSV file into a DataFrame
code_metrics = pd.read_csv('data/code_metrics.csv')

# Convert the first and last commit dates to datetime if not already
code_metrics['first_commit_date'] = pd.to_datetime(code_metrics['first_commit_date'], errors='coerce')
code_metrics['last_commit_date'] = pd.to_datetime(code_metrics['last_commit_date'], errors='coerce')

# Define the classification function
def classify_project(row):
    # Calculate project age and recent activity status
    now = datetime.now(timezone.utc)  # Make now timezone-aware
    project_age = (now - row['first_commit_date']).days if pd.notnull(row['first_commit_date']) else None
    recent_activity = (now - row['last_commit_date']).days if pd.notnull(row['last_commit_date']) else None
    
    # Category definitions
    if (row['star_count'] > 1000 and row['fork_count'] > 200 and 
        row['developer_count'] > 14 and row['contributor_count'] > 80 and 
        row['commit_count_6_months'] > 300 and recent_activity is not None and recent_activity <= 180):
        return 'High Popularity, Actively Maintained'
    
    elif (row['star_count'] > 1000 and row['fork_count'] > 200 and 
          6 <= row['developer_count'] <= 14 and 16 <= row['contributor_count'] <= 80 and 
          row['commit_count_6_months'] < 60 and project_age is not None and project_age > 730 and 
          recent_activity is not None and recent_activity > 180):
        return 'High Popularity, Low Maintenance'
    
    elif (60 <= row['star_count'] <= 1000 and 28 <= row['fork_count'] <= 200 and 
          row['developer_count'] > 6 and row['contributor_count'] > 16 and 
          row['commit_count_6_months'] > 300 and recent_activity is not None and recent_activity <= 180):
        return 'Niche, Actively Maintained'
    
    elif (6 <= row['star_count'] <= 60 and 3 <= row['fork_count'] <= 28 and 
          2 <= row['developer_count'] <= 6 and 4 <= row['contributor_count'] <= 16 and 
          row['commit_count_6_months'] > 60 and project_age is not None and project_age <= 730 and 
          recent_activity is not None and recent_activity <= 180):
        return 'New and Growing'
    
    elif (row['star_count'] > 1000 and row['fork_count'] > 200 and 
          row['developer_count'] < 6 and row['contributor_count'] < 16 and 
          row['commit_count_6_months'] < 60 and project_age is not None and project_age > 730 and 
          recent_activity is not None and recent_activity > 180):
        return 'Mature, Low Activity'
    
    elif (row['star_count'] < 6 and row['fork_count'] < 3 and 
          row['developer_count'] < 2 and row['contributor_count'] < 4 and 
          row['commit_count_6_months'] < 2 and recent_activity is not None and recent_activity > 365):
        return 'Inactive or Abandoned'
    
    else:
        return 'Uncategorized'

# Apply the classification function to each row
code_metrics['category'] = code_metrics.apply(classify_project, axis=1)

st.dataframe(code_metrics)

# Plot the 2x2 matrix using Plotly
fig = px.scatter(
    code_metrics,
    x='star_count',
    y='commit_count_6_months',
    color='category',
    title='2x2 Matrix of Open Source Project Categories',
    labels={'popularity': 'Popularity', 'activity': 'Activity Level'},
    color_discrete_map={
        'High Popularity, Actively Maintained': 'blue',
        'High Popularity, Low Maintenance': 'orange',
        'Niche, Actively Maintained': 'green',
        'New and Growing': 'purple',
        'Mature, Low Activity': 'red',
        'Inactive or Abandoned': 'gray',
        'Uncategorized': 'brown'
    }
)

# Display the plot in Streamlit
st.plotly_chart(fig)  # Use Streamlit to display the Plotly figure
