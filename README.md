# Client Priority Dashboard

Interactive dashboard for analyzing and prioritizing clients based on weighted factors.

## Quick Start for Users

1. Go to the deployed app URL (provided separately)
2. Upload your client rankings Excel file
3. Adjust the weight sliders to see how priorities shift
4. View tier breakdowns, score curves, and distributions

## File Format

Your Excel file should have these columns (exact names):
- **Client** - Client name
- **Current Client** - "Y" or "N" 
- **Current Work** - Score 0-10
- **Future Work** - Score 0-10
- **Difficulty Dealing With** - Score 0-10
- **Profitability** - Score 0-10
- **Ease to Distribute** - Score 0-10

See `client_rankings_template.xlsx` for an example.

## Deployment Instructions (For Admin)

### Step 1: Create GitHub Repository
1. Go to github.com and create account (free)
2. Click "+" → "New repository"
3. Name it `client-priority-dashboard`
4. Select **Public** (required for free Streamlit Cloud)
5. Click "Create repository"

### Step 2: Upload Files
Upload these 3 files to your repository:
- `client_dashboard.py` - The main application
- `requirements.txt` - Python dependencies
- `client_rankings_template.xlsx` - Example data file (optional)

### Step 3: Deploy to Streamlit Cloud
1. Go to share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `client-priority-dashboard`
5. Main file: `client_dashboard.py`
6. Click "Deploy"

Wait 2-3 minutes for deployment. You'll get a URL like:
`https://client-priority-dashboard-abc123.streamlit.app`

### Step 4: Share
Send the URL to anyone who needs access. They can:
- Upload their own client data file
- Adjust weights interactively
- View all analysis charts in real-time

**Important**: The code is public but your client data is NOT. Users upload files each session - nothing is stored on the server.

## Features

- **Weighted Scoring** - Adjust 5 factors with auto-normalizing weights
- **Natural Tier Detection** - Jenks algorithm finds optimal client groupings
- **Score Drop-Off Curve** - Visualize where priority breaks occur
- **Distribution Analysis** - Compare current vs non-current clients
- **Real-Time Updates** - All charts update instantly as you adjust weights

## Technical Details

- Built with Streamlit + Plotly
- Jenks natural breaks algorithm for tier detection
- Supports Excel (.xlsx, .xls) and CSV files
- No data persistence - files uploaded per session only
