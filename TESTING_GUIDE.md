# Testing Guide - Codebase Genius

This guide provides comprehensive instructions for testing the Codebase Genius system.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup for Testing](#setup-for-testing)
3. [Backend Testing](#backend-testing)
4. [Frontend Testing](#frontend-testing)
5. [Integration Testing](#integration-testing)
6. [Sample Test Cases](#sample-test-cases)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before testing, ensure you have:

- ✅ Python 3.8+ installed
- ✅ Git installed and in PATH
- ✅ OpenAI API key with available credits
- ✅ Internet connection for cloning repositories
- ✅ At least 2GB free disk space

---

## Setup for Testing

### 1. Environment Setup

```bash
# Navigate to project directory
cd codebase_genius/BE

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the `BE` directory:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Important:** Never commit your `.env` file to version control!

### 3. Verify Installation

```bash
# Check if jac is installed
jac --version

# Should output something like: Jac version x.x.x
```

---

## Backend Testing

### Test 1: Start the Jac Server

```bash
cd BE
jac serve main.jac
```

**Expected Output:**
```
Server running on http://localhost:8000
```

**Verification:**
- Server starts without errors
- No import errors
- Port 8000 is accessible

### Test 2: Health Check

Open a new terminal and test the server:

```bash
curl http://localhost:8000/docs
```

**Expected:** API documentation page or confirmation that server is running.

---

## API Endpoint Testing

### Test 3: Generate Documentation (Small Repository)

Test with a small, well-documented repository:

```bash
curl -X POST http://localhost:8000/walker/code_genius \
  -H "Content-Type: application/json" \
  -d "{\"github_url\": \"https://github.com/pallets/flask\"}"
```

**Expected Response:**
```json
{
  "reports": [
    {
      "status": "completed",
      "repository": "flask",
      "documentation_path": "outputs/flask/docs.md",
      "message": "Documentation generated successfully"
    }
  ]
}
```

**Verification Checklist:**
- ✅ Response status is 200
- ✅ Status field is "completed"
- ✅ Documentation file is created in `outputs/flask/docs.md`
- ✅ File contains markdown content
- ✅ No error messages in server logs

### Test 4: Retrieve Generated Documentation

```bash
curl -X POST http://localhost:8000/walker/get_documentation \
  -H "Content-Type: application/json" \
  -d "{\"repo_name\": \"flask\"}"
```

**Expected Response:**
```json
{
  "reports": [
    {
      "status": "success",
      "content": "# flask - Documentation\n\n..."
    }
  ]
}
```

**Verification:**
- ✅ Content field contains markdown
- ✅ Documentation includes all sections (Overview, Installation, Architecture, API Reference)

### Test 5: List All Repositories

```bash
curl -X POST http://localhost:8000/walker/list_repositories \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "reports": [
    [
      {
        "name": "flask",
        "url": "https://github.com/pallets/flask",
        "status": "completed"
      }
    ]
  ]
}
```

---

## Frontend Testing

### Test 6: Start Streamlit Application

```bash
cd FE
pip install -r requirements.txt
streamlit run app.py
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

**Verification:**
- ✅ Application opens in browser
- ✅ UI loads without errors
- ✅ All tabs are visible (Generate, View, History)

### Test 7: UI Functionality Test

1. **Generate Documentation Tab**
   - Enter URL: `https://github.com/psf/requests`
   - Click "Generate Docs"
   - Wait for processing (2-5 minutes)
   - Verify success message appears
   - Check that documentation path is displayed

2. **View Documentation Tab**
   - Enter repository name: `requests`
   - Click "View Docs"
   - Verify markdown is rendered correctly
   - Test download button

3. **Repository History Tab**
   - Click "Refresh List"
   - Verify repositories are displayed
   - Check status badges are correct

---

## Integration Testing

### Test 8: End-to-End Workflow

This test validates the complete workflow from URL input to documentation output.

**Steps:**

1. **Start Backend**
   ```bash
   cd BE
   jac serve main.jac
   ```

2. **Start Frontend** (new terminal)
   ```bash
   cd FE
   streamlit run app.py
   ```

3. **Generate Documentation**
   - Open `http://localhost:8501`
   - Enter: `https://github.com/kennethreitz/requests`
   - Click "Generate Docs"
   - Wait for completion

4. **Verify Output**
   ```bash
   # Check file exists
   ls outputs/requests/docs.md
   
   # View content
   cat outputs/requests/docs.md
   ```

5. **Verify Content Quality**
   - ✅ Table of Contents present
   - ✅ Overview section with project description
   - ✅ Installation instructions
   - ✅ Architecture diagram (Mermaid format)
   - ✅ API Reference with functions/classes
   - ✅ Proper markdown formatting

---

## Sample Test Cases

### Test Case 1: Python Repository

**Repository:** `https://github.com/psf/requests`
**Expected Time:** 3-5 minutes
**Expected Outcome:** 
- Documentation with Python functions and classes
- Mermaid diagrams showing class relationships
- Installation instructions from README

### Test Case 2: Small Repository

**Repository:** `https://github.com/pallets/flask`
**Expected Time:** 2-3 minutes
**Expected Outcome:**
- Quick processing
- Complete documentation
- All sections populated

### Test Case 3: Jac Repository

**Repository:** `https://github.com/jaseci-labs/jaclang`
**Expected Time:** 5-10 minutes
**Expected Outcome:**
- Jac-specific parsing (walkers, nodes)
- Architecture showing Jac constructs
- Proper handling of Jac syntax

### Test Case 4: Invalid URL

**Input:** `https://github.com/invalid/nonexistent`
**Expected Outcome:**
- Error message: "Repository not found" or "Clone failed"
- No crash
- Graceful error handling

### Test Case 5: Private Repository

**Input:** `https://github.com/private/repo`
**Expected Outcome:**
- Error message about access
- Suggestion to use public repositories
- No system crash

---

## Error Testing

### Test 9: Invalid GitHub URL

```bash
curl -X POST http://localhost:8000/walker/code_genius \
  -H "Content-Type: application/json" \
  -d "{\"github_url\": \"not-a-valid-url\"}"
```

**Expected Response:**
```json
{
  "status": "error",
  "message": "Invalid GitHub URL provided"
}
```

### Test 10: Missing API Key

1. Remove or rename `.env` file
2. Restart server
3. Try to generate documentation

**Expected:** Error about missing API key

### Test 11: Network Failure Simulation

1. Disconnect internet
2. Try to clone repository

**Expected:** Graceful error message about network connectivity

---

## Performance Testing

### Test 12: Large Repository

**Repository:** `https://github.com/django/django`
**Purpose:** Test system with large codebase
**Expected:** 
- Processing time: 10-15 minutes
- Memory usage: < 2GB
- No crashes
- Complete documentation

### Test 13: Concurrent Requests

Test multiple simultaneous documentation requests:

```bash
# Terminal 1
curl -X POST http://localhost:8000/walker/code_genius \
  -H "Content-Type: application/json" \
  -d "{\"github_url\": \"https://github.com/pallets/flask\"}" &

# Terminal 2
curl -X POST http://localhost:8000/walker/code_genius \
  -H "Content-Type: application/json" \
  -d "{\"github_url\": \"https://github.com/psf/requests\"}" &
```

**Expected:** Both requests complete successfully (may take longer)

---

## Quality Verification

### Documentation Quality Checklist

For each generated documentation, verify:

- [ ] **Completeness**
  - [ ] Table of Contents present
  - [ ] All sections included
  - [ ] No placeholder text

- [ ] **Accuracy**
  - [ ] Function signatures correct
  - [ ] Class names accurate
  - [ ] Import statements valid

- [ ] **Formatting**
  - [ ] Valid markdown syntax
  - [ ] Code blocks properly formatted
  - [ ] Headers hierarchical

- [ ] **Diagrams**
  - [ ] Mermaid syntax valid
  - [ ] Relationships accurate
  - [ ] Readable and clear

- [ ] **Readability**
  - [ ] Clear descriptions
  - [ ] Logical organization
  - [ ] Professional tone

---

## Automated Testing Script

Create a test script `test_system.sh`:

```bash
#!/bin/bash

echo "=== Codebase Genius Test Suite ==="
echo ""

# Test 1: Server Health
echo "Test 1: Server Health Check"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
if [ $response -eq 200 ]; then
    echo "✅ Server is running"
else
    echo "❌ Server not responding"
    exit 1
fi

# Test 2: Generate Documentation
echo ""
echo "Test 2: Generate Documentation"
response=$(curl -s -X POST http://localhost:8000/walker/code_genius \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/pallets/flask"}')

if echo "$response" | grep -q "completed"; then
    echo "✅ Documentation generated"
else
    echo "❌ Documentation generation failed"
    echo "$response"
fi

# Test 3: Retrieve Documentation
echo ""
echo "Test 3: Retrieve Documentation"
response=$(curl -s -X POST http://localhost:8000/walker/get_documentation \
  -H "Content-Type: application/json" \
  -d '{"repo_name": "flask"}')

if echo "$response" | grep -q "success"; then
    echo "✅ Documentation retrieved"
else
    echo "❌ Documentation retrieval failed"
fi

# Test 4: List Repositories
echo ""
echo "Test 4: List Repositories"
response=$(curl -s -X POST http://localhost:8000/walker/list_repositories \
  -H "Content-Type: application/json")

if echo "$response" | grep -q "flask"; then
    echo "✅ Repository list retrieved"
else
    echo "❌ Repository list failed"
fi

echo ""
echo "=== Test Suite Complete ==="
```

Run with:
```bash
chmod +x test_system.sh
./test_system.sh
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "jac: command not found"

**Solution:**
```bash
pip install --upgrade jac-cloud
```

#### Issue 2: "Port 8000 already in use"

**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

#### Issue 3: Git clone fails

**Solution:**
- Verify Git is installed: `git --version`
- Check internet connection
- Try cloning manually: `git clone <url>`

#### Issue 4: OpenAI API errors

**Solution:**
- Verify API key is correct
- Check API credits/quota
- Test API key: 
  ```bash
  curl https://api.openai.com/v1/models \
    -H "Authorization: Bearer $OPENAI_API_KEY"
  ```

#### Issue 5: Import errors in Jac

**Solution:**
```bash
pip uninstall byllm jac-cloud
pip install byllm jac-cloud
```

#### Issue 6: Streamlit not loading

**Solution:**
```bash
streamlit cache clear
streamlit run app.py --server.port 8502
```

---

## Test Results Template

Use this template to document your test results:

```markdown
## Test Results - [Date]

### Environment
- OS: Windows/macOS/Linux
- Python Version: 
- Jac Version: 
- OpenAI Model: gpt-4o

### Test Summary
- Total Tests: 
- Passed: ✅
- Failed: ❌
- Skipped: ⏭️

### Detailed Results

#### Test 1: Server Startup
- Status: ✅/❌
- Time: X seconds
- Notes: 

#### Test 2: Documentation Generation
- Repository: 
- Status: ✅/❌
- Time: X minutes
- Output Quality: Good/Fair/Poor
- Notes:

[Continue for all tests...]

### Issues Found
1. [Issue description]
2. [Issue description]

### Recommendations
- [Recommendation 1]
- [Recommendation 2]
```

---

## Continuous Testing

For ongoing development, set up continuous testing:

1. **Daily Health Checks**
   - Run automated test script
   - Verify all endpoints
   - Check documentation quality

2. **Weekly Full Tests**
   - Test with multiple repositories
   - Verify all features
   - Performance benchmarking

3. **Before Deployment**
   - Complete test suite
   - Code review
   - Documentation review

---

## Success Criteria

The system passes testing if:

- ✅ All API endpoints respond correctly
- ✅ Documentation is generated for 3+ test repositories
- ✅ No crashes or unhandled exceptions
- ✅ Output quality meets standards
- ✅ Frontend UI is functional
- ✅ Error handling works properly
- ✅ Performance is acceptable (< 10 min for medium repos)

---

## Next Steps After Testing

1. **Document Issues**: Record any bugs or issues found
2. **Optimize Performance**: Identify bottlenecks
3. **Improve Quality**: Enhance documentation output
4. **Add Features**: Implement additional capabilities
5. **Deploy**: Prepare for production deployment

---

*Happy Testing! 🧪*
