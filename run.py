import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timezone

# Read the CSV file into a DataFrame
code_metrics = pd.read_csv('data/code_metrics.csv')

# Convert the first and last commit dates to datetime if not already
code_metrics['first_commit_date'] = pd.to_datetime(code_metrics['first_commit_date'], errors='coerce')
code_metrics['last_commit_date'] = pd.to_datetime(code_metrics['last_commit_date'], errors='coerce')

# Function to calculate thresholds dynamically based on user-selected collection
def calculate_thresholds(df):
    thresholds = {
        'star_count': df['star_count'].median(),
        'fork_count': df['fork_count'].median(),
        'commit_count_6_months': df['commit_count_6_months'].median(),
        'developer_count': df['developer_count'].median(),
        'contributor_count': df['contributor_count'].median(),
    }
    return thresholds

# Define the classification function based on calculated thresholds
def classify_project(row, thresholds):
    # Calculate recent activity in days
    now = datetime.now(timezone.utc)
    recent_activity = (now - row['last_commit_date']).days if pd.notnull(row['last_commit_date']) else None
    
    # Determine parameter levels based on thresholds
    popularity = 'High' if row['star_count'] > thresholds['star_count'] or row['fork_count'] > thresholds['fork_count'] else 'Low'
    activity = 'High' if row['commit_count_6_months'] > thresholds['commit_count_6_months'] or (recent_activity is not None and recent_activity <= 180) else 'Low'
    size = 'Large' if row['developer_count'] > thresholds['developer_count'] or row['contributor_count'] > thresholds['contributor_count'] else 'Small'

    # Assign categories based on the parameter levels
    if popularity == 'High' and activity == 'High' and size == 'Large':
        return 'High Popularity, High Activity, Large Size'
    elif popularity == 'High' and activity == 'High' and size == 'Small':
        return 'High Popularity, High Activity, Small Size'
    elif popularity == 'High' and activity == 'Low' and size == 'Large':
        return 'High Popularity, Low Activity, Large Size'
    elif popularity == 'High' and activity == 'Low' and size == 'Small':
        return 'High Popularity, Low Activity, Small Size'
    elif popularity == 'Low' and activity == 'High' and size == 'Large':
        return 'Low Popularity, High Activity, Large Size'
    elif popularity == 'Low' and activity == 'High' and size == 'Small':
        return 'Low Popularity, High Activity, Small Size'

# Streamlit interface for collection selection
st.title("Open Source Project Categorization")

# Create a filter for user to select a value from collection_name
selected_collection = st.selectbox("Select Collection Name", code_metrics['collection_name'].unique())

# Filter the DataFrame based on the selected collection
filtered_code_metrics = code_metrics[code_metrics['collection_name'] == selected_collection]

# Calculate thresholds based on filtered data
thresholds = calculate_thresholds(filtered_code_metrics)

# Apply the classification function with dynamic thresholds
filtered_code_metrics['category'] = filtered_code_metrics.apply(lambda row: classify_project(row, thresholds), axis=1)

# Display the categorized data
st.dataframe(filtered_code_metrics)

# Plot the 2x2 matrix using Plotly
fig = px.scatter(
    filtered_code_metrics,
    x='star_count',
    y='commit_count_6_months',
    color='category',
    title='2x2 Matrix of Open Source Project Categories',
    labels={'star_count': 'Star Count (Popularity)', 'commit_count_6_months': 'Commit Count (Activity)'},
    color_discrete_map={
        'High Popularity, High Activity, Large Size': 'blue',
        'High Popularity, High Activity, Small Size': 'orange',
        'High Popularity, Low Activity, Large Size': 'green',
        'High Popularity, Low Activity, Small Size': 'purple',
        'Low Popularity, High Activity, Large Size': 'red',
        'Low Popularity, High Activity, Small Size': 'gray',
    }
)

# Update layout for size and log scale
fig.update_layout(
    width=800,  # Increase width
    height=600,  # Increase height
)

# Set axes to logarithmic scale
fig.update_xaxes(type="log")  # Set x-axis to log scale
fig.update_yaxes(type="log")  # Set y-axis to log scale

# Display the plot in Streamlit
st.plotly_chart(fig)
