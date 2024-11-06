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

# Define the desired category order
desired_order = [
    'High Popularity, Actively Maintained',
    'High Popularity, Low Maintenance',
    'Niche, Actively Maintained',
    'New and Growing',
    'Moderately Maintained',
    'Mature, Low Activity',
    'Moderate Popularity, Low Activity',
    'Low Popularity, Low Activity',
    'Inactive or Abandoned',
    'Uncategorized'
]

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
    options=[""] + sorted(code_metrics['collection_name'].unique().tolist()),  # Sort the collection names alphabetically
    format_func=lambda x: "Select a Collection" if x == "" else x
)

# Step 2: Filter based on the selected collection and apply classification
if selected_collection:
    filtered_code_metrics = code_metrics[code_metrics['collection_name'] == selected_collection]
    filtered_code_metrics['category'] = filtered_code_metrics.apply(classify_project, axis=1)

    fig_treemap = px.treemap(
        filtered_code_metrics,
        path=['category', 'display_name'],
        values='developer_count',
        color='category',
        color_discrete_map={
        'High Popularity, Actively Maintained': '#87CEEB',  # Light Sky Blue
        'High Popularity, Low Maintenance': '#FFDAB9',      # Soft Peach
        'Niche, Actively Maintained': '#E6E6FA',            # Lavender
        'New and Growing': '#98FF98',                       # Mint Green
        'Moderately Maintained': '#B2DFDB',                 # Light Seafoam
        'Mature, Low Activity': '#FFF5BA',                  # Light Sand
        'Moderate Popularity, Low Activity': '#FFCCCB',     # Pale Rose
        'Low Popularity, Low Activity': '#D3D3D3',          # Light Gray
        'Inactive or Abandoned': '#F5F5DC',                 # Very Light Beige
        'Uncategorized': '#B0C4DE'                          # Light Slate Gray
        },
        title=f"Project Distribution by Category in '{selected_collection}'"
    )

    fig_treemap.update_layout(
        width=800,  # Set width to make the chart square
        height=800,  # Set height to match width
        margin=dict(t=40, l=0, r=0, b=0)
    )

    # Increase font size for the first level (category)
    fig_treemap.update_traces(textfont=dict(size=18))  # Adjust size as desired

    # Count projects by category
    category_counts = filtered_code_metrics['category'].value_counts().reindex(desired_order, fill_value=0)

    # Create bar chart
    fig_bar = px.bar(
        x=category_counts.values,
        y=category_counts.index,
        orientation='h',
        labels={'x': 'Number of Projects', 'y': 'Category'},
        color=category_counts.index,
        color_discrete_map={
            'High Popularity, Actively Maintained': '#87CEEB',
            'High Popularity, Low Maintenance': '#FFDAB9',
            'Niche, Actively Maintained': '#E6E6FA',
            'New and Growing': '#98FF98',
            'Moderately Maintained': '#B2DFDB',
            'Mature, Low Activity': '#FFF5BA',
            'Moderate Popularity, Low Activity': '#FFCCCB',
            'Low Popularity, Low Activity': '#D3D3D3',
            'Inactive or Abandoned': '#F5F5DC',
            'Uncategorized': '#B0C4DE'
        },
        title="Number of Projects by Category"
    )
    fig_bar.update_layout(showlegend=False)
    
    # Centering the treemap using Streamlit columns
    col1, col2, col3 = st.columns([1, 3, 1])  # The middle column is wider to center the chart
    with col2:
        st.plotly_chart(fig_bar)
        st.plotly_chart(fig_treemap)
    
    # Step 3: Show the Category selection only after Collection is selected
    categories = filtered_code_metrics['category'].unique().tolist()

    # Filter the categories list based on the ones that exist in the data, keeping the specified order
    ordered_categories = [cat for cat in desired_order if cat in categories]

    
    # Use a selectbox instead of radio buttons to allow an unselected initial state
    #selected_category = st.selectbox(
    #    "Select Category",
    #    options=[""] + ["All"] + ordered_categories,  # Add an empty string as the first option, followed by "All" and the categories
    #    format_func=lambda x: "Please select a category" if x == "" else x
    #)

    # Define available categories with an "All" option
    category_options = ["All"] + ordered_categories
    
    # Use st.multiselect for multi-selection
    selected_categories = st.multiselect(
        "Select Categories",
        options=category_options,
        default=[],  # Start with "All" selected, or set to [] for no pre-selection
        format_func=lambda x: "All Categories" if x == "All" else x
    )
    
    # Filter the DataFrame only if a valid category is selected
    if selected_categories and selected_categories != "":
        #if selected_category != "All":
        #    filtered_code_metrics = filtered_code_metrics[filtered_code_metrics['category'] == selected_category]

        # Handle the "All" selection by including all categories if "All" is selected
        if "All" in selected_categories:
            filtered_categories = ordered_categories  # Use all categories if "All" is selected
        else:
            filtered_categories = selected_categories  # Otherwise, use the selected categories
        
        # Filter the DataFrame based on the selected categories
        filtered_code_metrics = filtered_code_metrics[filtered_code_metrics['category'].isin(filtered_categories)]
            
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
                'High Popularity, Actively Maintained': '#4682B4',  # Sky Blue
                'High Popularity, Low Maintenance': '#FFB07C',      # Peach
                'Niche, Actively Maintained': '#9370DB',            # Lavender Purple
                'New and Growing': '#3CB371',                       # Mint
                'Moderately Maintained': '#66CDAA',                 # Seafoam Green
                'Mature, Low Activity': '#D2B48C',                  # Sand
                'Moderate Popularity, Low Activity': '#FF6F61',     # Rose
                'Low Popularity, Low Activity': '#A9A9A9',          # Gray
                'Inactive or Abandoned': '#CDC5B4',                 # Beige
                'Uncategorized': '#778899'                          # Slate Gray
            },
            text='display_name'
        )
    
        fig.update_traces(textposition='top center')
        fig.update_layout(width=1200, height=900, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        fig.update_xaxes(type="log")
        fig.update_yaxes(type="log")
    
        # Display the plot
        st.plotly_chart(fig)


        # Convert the 'category' column to a categorical type with the desired order
        filtered_code_metrics['category'] = pd.Categorical(
            filtered_code_metrics['category'], 
            categories=desired_order, 
            ordered=True
        )
        
        # Sort the DataFrame by the 'category' column
        filtered_code_metrics = filtered_code_metrics.sort_values('category')
        # Format the dates to 'dd-MON-YYYY'
        filtered_code_metrics['first_commit_date'] = filtered_code_metrics['first_commit_date'].dt.strftime('%d-%b-%Y')
        filtered_code_metrics['last_commit_date'] = filtered_code_metrics['last_commit_date'].dt.strftime('%d-%b-%Y')

        
        # Define the column order
        column_order = [
            'category',
            'display_name', 
            'star_count', 
            'fork_count', 
            'first_commit_date', 
            'last_commit_date', 
            'developer_count', 
            'contributor_count', 
            'active_developer_count_6_months', 
            'commit_count_6_months', 
            'merged_pull_request_count_6_months', 
            'closed_issue_count_6_months'
        ]
        
        # Display the DataFrame in the specified column order
        st.dataframe(filtered_code_metrics[column_order])

 
