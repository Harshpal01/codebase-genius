# Codebase Genius - Frontend

This is the Streamlit-based frontend for Codebase Genius.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

## Features

- **Generate Documentation**: Enter a GitHub URL and generate comprehensive documentation
- **View Documentation**: Browse and download generated documentation
- **Repository History**: View all processed repositories

## Usage

1. Ensure the backend server is running at `http://localhost:8000`
2. Launch the Streamlit app
3. Navigate to the "Generate Documentation" tab
4. Enter a GitHub repository URL
5. Click "Generate Docs" and wait for processing
6. View the generated documentation in the "View Documentation" tab

## Requirements

- Backend server must be running
- Internet connection for cloning repositories
- Valid OpenAI API key configured in backend
