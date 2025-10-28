# Codebase Genius - Backend

This is the backend implementation of **Codebase Genius**, an agentic AI system that automatically generates comprehensive documentation for software repositories.

## Architecture

The system uses a multi-agent architecture built with JacLang:

### Agents

1. **Code Genius (Supervisor)** - Orchestrates the entire workflow
2. **Repo Mapper** - Clones repositories, builds file trees, and summarizes READMEs
3. **Code Analyzer** - Parses source code and builds Code Context Graphs (CCG)
4. **DocGenie** - Generates comprehensive markdown documentation with diagrams

### Technology Stack

- **JacLang** - Primary programming language
- **byLLM** - Multi-tool prompting framework
- **OpenAI GPT-4** - Language model for intelligent analysis
- **Python AST** - Python code parsing
- **Git** - Repository cloning

---

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Git installed and accessible from command line
- OpenAI API key (or Gemini API key)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd codebase_genius/BE
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `BE` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 5. Run the Jac Server

```bash
jac serve main.jac
```

This will start a local server at `http://localhost:8000`.

---

## API Usage

### Generate Documentation for a Repository

**Endpoint:** `POST /walker/code_genius`

**Request Body:**
```json
{
  "github_url": "https://github.com/username/repository"
}
```

**Response:**
```json
{
  "reports": [
    {
      "status": "completed",
      "repository": "repository",
      "documentation_path": "outputs/repository/docs.md",
      "message": "Documentation generated successfully"
    }
  ]
}
```

### Get Generated Documentation

**Endpoint:** `POST /walker/get_documentation`

**Request Body:**
```json
{
  "repo_name": "repository"
}
```

**Response:**
```json
{
  "reports": [
    {
      "status": "success",
      "content": "# Repository Documentation\n..."
    }
  ]
}
```

### List All Repositories

**Endpoint:** `POST /walker/list_repositories`

**Response:**
```json
{
  "reports": [
    [
      {
        "name": "repository1",
        "url": "https://github.com/user/repo1",
        "status": "completed"
      }
    ]
  ]
}
```

---

## Testing the System

### Example: Generate Documentation for a Sample Repository

```bash
curl -X POST http://localhost:8000/walker/code_genius \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/psf/requests"}'
```

The generated documentation will be saved to:
```
outputs/requests/docs.md
```

---

## Project Structure

```
BE/
├── main.jac              # Main application with all agents
├── utils.jac             # Utility functions
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md            # This file
```

---

## How It Works

### Workflow

1. **Repository Cloning**
   - Validates GitHub URL
   - Clones repository to `temp_repos/`
   
2. **Repository Mapping**
   - Builds hierarchical file tree
   - Identifies and summarizes README
   - Determines entry point files

3. **Code Analysis**
   - Parses Python files using AST
   - Parses Jac files using regex patterns
   - Extracts functions, classes, methods, walkers, nodes
   - Builds Code Context Graph showing relationships

4. **Documentation Generation**
   - Generates overview section
   - Creates installation instructions
   - Produces API reference
   - Generates Mermaid architecture diagrams
   - Assembles complete markdown document

5. **Output**
   - Saves documentation to `outputs/<repo_name>/docs.md`
   - Returns path and status

---

## Supported Languages

- **Python** (.py files) - Full AST parsing
- **Jac** (.jac files) - Pattern-based parsing

The system can be extended to support additional languages by adding new parser functions.

---

## Error Handling

The system handles various error scenarios:

- Invalid GitHub URLs
- Private repositories (requires authentication)
- Cloning failures
- Parsing errors
- Missing README files

All errors are reported with descriptive messages.

---

## Extending the System

### Adding Support for New Languages

1. Create a parser function in `utils.jac`:
   ```jac
   def parse_javascript_file(file_path: str) -> dict {
       // Your parsing logic
   }
   ```

2. Add the language to `CodeAnalyzer.supported_languages`

3. Update the `analyze_file` method to handle the new language

### Adding New Analysis Features

You can extend the `CodeAnalyzer` node with additional analysis capabilities:

- Cyclomatic complexity calculation
- Code quality metrics
- Dependency analysis
- Security vulnerability detection

---

## Troubleshooting

### Common Issues

**Issue:** `jac: command not found`
- **Solution:** Ensure `jac-cloud` is installed: `pip install jac-cloud`

**Issue:** Git clone fails
- **Solution:** Ensure Git is installed and accessible from command line

**Issue:** OpenAI API errors
- **Solution:** Verify your API key is correct and has sufficient credits

**Issue:** Import errors
- **Solution:** Ensure all dependencies are installed: `pip install -r requirements.txt`

---

## Performance Considerations

- Large repositories may take several minutes to process
- The system uses GPT-4 which has rate limits
- Documentation quality improves with well-structured codebases
- README files significantly improve output quality

---

## License

This project is part of an academic assignment for learning agentic AI systems.

---

## Contact

For questions or issues, please refer to the main project repository.
