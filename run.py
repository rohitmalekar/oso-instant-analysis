import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timezone

st.set_page_config(page_title="OSO Instant Analysis", layout="wide")

# Read the CSV file into a DataFrame
code_metrics = pd.read_csv('data/code_metrics.csv')

# Convert the first and last commit dates to datetime if not already
code_metrics['first_commit_date'] = pd.to_datetime(code_metrics['first_commit_date'], errors='coerce')
code_metrics['last_commit_date'] = pd.to_datetime(code_metrics['last_commit_date'], errors='coerce')

# Define the classification function with specified criteria
def classify_project(row):
    now = datetime.now(timezone.utc)
    project_age = (now - row['first_commit_date']).days if pd.notnull(row['first_commit_date']) else None
    recent_activity = (now - row['last_commit_date']).days if pd.notnull(row['last_commit_date']) else None

    if (row['star_count'] > 200 and row['fork_count'] > 100 and 
        row['developer_count'] > 10 and row['contributor_count'] > 50 and 
        row['commit_count_6_months'] > 200 and recent_activity is not None and recent_activity <= 180):
        return 'High Popularity, Actively Maintained'
    elif (row['star_count'] > 200 and row['fork_count'] > 100 and 
          4 <= row['developer_count'] <= 10 and 10 <= row['contributor_count'] <= 50 and 
          row['commit_count_6_months'] < 30 and project_age is not None and project_age > 730 and 
          recent_activity is not None and recent_activity > 180):
        return 'High Popularity, Low Maintenance'
    elif (30 <= row['star_count'] <= 200 and 10 <= row['fork_count'] <= 100 and 
          row['developer_count'] > 4 and row['contributor_count'] > 10 and 
          row['commit_count_6_months'] > 200 and recent_activity is not None and recent_activity <= 180):
        return 'Niche, Actively Maintained'
    elif (2 <= row['star_count'] <= 30 and 1 <= row['fork_count'] <= 10 and 
          1 <= row['developer_count'] <= 4 and 2 <= row['contributor_count'] <= 10 and 
          row['commit_count_6_months'] > 30 and project_age is not None and project_age <= 730 and 
          recent_activity is not None and recent_activity <= 180):
        return 'New and Growing'
    elif (row['star_count'] > 200 and row['fork_count'] > 100 and 
          row['developer_count'] < 4 and row['contributor_count'] < 10 and 
          row['commit_count_6_months'] < 30 and project_age is not None and project_age > 730 and 
          recent_activity is not None and recent_activity > 180):
        return 'Mature, Low Activity'
    elif (row['star_count'] < 2 and row['fork_count'] < 1 and 
          row['developer_count'] < 1 and row['contributor_count'] < 2 and 
          row['commit_count_6_months'] < 1 and recent_activity is not None and recent_activity > 365):
        return 'Inactive or Abandoned'
    elif (row['star_count'] < 30 and row['fork_count'] < 10 and 
          row['developer_count'] <= 4 and row['contributor_count'] <= 15 and 
          row['commit_count_6_months'] <= 12):
        return 'Low Popularity, Low Activity'
    elif (7 <= row['star_count'] <= 200 and 3 <= row['fork_count'] <= 70 and 
          2 <= row['developer_count'] <= 9 and 5 <= row['contributor_count'] <= 34 and 
          row['commit_count_6_months'] <= 23):
        return 'Moderate Popularity, Low Activity'
    elif row['commit_count_6_months'] > 50 and recent_activity is not None and recent_activity <= 180:
        return 'Moderately Maintained'
    else:
        return 'Uncategorized'

st.title("Open Source Observer - Instant Analytics")

# Step 1: Create a filter for the user to select a Collection Name
selected_collection = st.selectbox(
    "Select Collection Name",
    options=[""] + code_metrics['collection_name'].unique().tolist(),
    format_func=lambda x: "Select a Collection" if x == "" else x
)


# Step 2: Filter based on the selected collection and apply classification
if selected_collection:
    filtered_code_metrics = code_metrics[code_metrics['collection_name'] == selected_collection]
    filtered_code_metrics['category'] = filtered_code_metrics.apply(classify_project, axis=1)
    
    # Step 3: Show the Category selection only after Collection is selected
    categories = filtered_code_metrics['category'].unique().tolist()
    selected_category = st.radio("Select Category", options=['All'] + categories)  # Using radio button as suggested

    # Step 4: Further filter based on selected category
    if selected_category != 'All':
        filtered_code_metrics = filtered_code_metrics[filtered_code_metrics['category'] == selected_category]

    # Display the categorized data
    st.dataframe(filtered_code_metrics)

    # Calculate the new Y-axis value for the plot
    filtered_code_metrics['commit_per_active_dev'] = (
        filtered_code_metrics['commit_count_6_months'] / 
        filtered_code_metrics['active_developer_count_6_months']
    ).fillna(0)  # Fill NaN values with 0 if any

    # Step 5: Plot the 2x2 matrix using Plotly
    fig = px.scatter(
        filtered_code_metrics,
        x='star_count',
        y='commit_per_active_dev',  # Use the new column for Y-axis
        color='category',
        title='2x2 Matrix of Open Source Project Categories',
        labels={'star_count': 'Star Count (Popularity)', 'commit_per_active_dev': 'Commits per Active Developer'},
        color_discrete_map={
            'High Popularity, Actively Maintained': 'blue',
            'High Popularity, Low Maintenance': 'orange',
            'Niche, Actively Maintained': 'green',
            'New and Growing': 'purple',
            'Mature, Low Activity': 'red',
            'Inactive or Abandoned': 'gray',
            'Low Popularity, Low Activity': 'brown',
            'Moderate Popularity, Low Activity': 'pink',
            'Moderately Maintained': 'cyan',
            'Uncategorized': 'black'
        },
        text='display_name'
    )

    fig.update_traces(textposition='top center')
    fig.update_layout(width=1200, height=900, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
    fig.update_xaxes(type="log")
    fig.update_yaxes(type="log")

    # Display the plot
    st.plotly_chart(fig)
