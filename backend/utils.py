"""
Utility functions for Codebase Genius
Handles git operations, file parsing, and code analysis
"""

import os
import ast
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


# ============================================
# GIT OPERATIONS
# ============================================

def validate_github_url(url: str) -> bool:
    """Validate if URL is a valid GitHub repository URL"""
    pattern = r'^https?://github\.com/[\w-]+/[\w.-]+/?$'
    return bool(re.match(pattern, url.rstrip('.git')))


def clone_repository(url: str, target_dir: str) -> Dict[str, any]:
    """Clone a GitHub repository to target directory"""
    try:
        # Create target directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # Clone the repository
        result = subprocess.run(
            ['git', 'clone', url, target_dir],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "path": target_dir,
                "message": "Repository cloned successfully"
            }
        else:
            return {
                "success": False,
                "path": None,
                "message": f"Clone failed: {result.stderr}"
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "path": None,
            "message": "Clone operation timed out"
        }
    except Exception as e:
        return {
            "success": False,
            "path": None,
            "message": f"Error: {str(e)}"
        }


def extract_repo_name(url: str) -> str:
    """Extract repository name from GitHub URL"""
    parts = url.rstrip('/').rstrip('.git').split('/')
    return parts[-1]


# ============================================
# FILE SYSTEM OPERATIONS
# ============================================

IGNORED_DIRS = {
    '.git', '.github', 'node_modules', '__pycache__', '.pytest_cache',
    'venv', 'env', '.env', '.venv', 'dist', 'build', '.idea', '.vscode',
    '.egg-info', 'htmlcov', '.tox', '.mypy_cache', '.coverage'
}

IGNORED_FILES = {
    '.DS_Store', 'Thumbs.db', '.gitignore', '.gitattributes',
    '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.dylib'
}


def build_file_tree(root_path: str, max_depth: int = 5) -> Dict:
    """Build a structured file tree representation"""
    def should_ignore(name: str) -> bool:
        return name in IGNORED_DIRS or any(name.endswith(ext) for ext in ['.pyc', '.pyo', '.pyd'])
    
    def traverse(path: str, depth: int = 0) -> Dict:
        if depth > max_depth:
            return {}
        
        tree = {"type": "directory", "children": {}}
        
        try:
            for item in sorted(os.listdir(path)):
                if should_ignore(item):
                    continue
                
                item_path = os.path.join(path, item)
                
                if os.path.isdir(item_path):
                    tree["children"][item] = traverse(item_path, depth + 1)
                else:
                    # Get file info
                    size = os.path.getsize(item_path)
                    ext = os.path.splitext(item)[1]
                    tree["children"][item] = {
                        "type": "file",
                        "size": size,
                        "extension": ext
                    }
        except PermissionError:
            pass
        
        return tree
    
    return traverse(root_path)


def find_readme(repo_path: str) -> Optional[str]:
    """Find and read README file"""
    readme_names = ['README.md', 'README.rst', 'README.txt', 'README', 'readme.md']
    
    for name in readme_names:
        readme_path = os.path.join(repo_path, name)
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                continue
    
    return None


def find_entry_points(repo_path: str) -> List[str]:
    """Find main entry point files"""
    entry_patterns = ['main.py', 'app.py', '__main__.py', 'run.py', 'server.py', 'main.jac']
    entry_files = []
    
    for root, dirs, files in os.walk(repo_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        
        for file in files:
            if file in entry_patterns:
                entry_files.append(os.path.join(root, file))
    
    return entry_files


def get_python_files(repo_path: str) -> List[str]:
    """Get all Python files in repository"""
    python_files = []
    
    for root, dirs, files in os.walk(repo_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files


def get_jac_files(repo_path: str) -> List[str]:
    """Get all Jac files in repository"""
    jac_files = []
    
    for root, dirs, files in os.walk(repo_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        
        for file in files:
            if file.endswith('.jac'):
                jac_files.append(os.path.join(root, file))
    
    return jac_files


# ============================================
# PYTHON CODE PARSING
# ============================================

def parse_python_file(file_path: str) -> Dict:
    """Parse Python file and extract structure"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        result = {
            "file": file_path,
            "functions": [],
            "classes": [],
            "imports": [],
            "docstring": ast.get_docstring(tree)
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                result["functions"].append({
                    "name": node.name,
                    "line_start": node.lineno,
                    "line_end": node.end_lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node),
                    "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list]
                })
            
            elif isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                result["classes"].append({
                    "name": node.name,
                    "line_start": node.lineno,
                    "line_end": node.end_lineno,
                    "methods": methods,
                    "bases": [b.id if isinstance(b, ast.Name) else str(b) for b in node.bases],
                    "docstring": ast.get_docstring(node)
                })
            
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append({
                        "module": alias.name,
                        "alias": alias.asname
                    })
            
            elif isinstance(node, ast.ImportFrom):
                result["imports"].append({
                    "module": node.module,
                    "names": [alias.name for alias in node.names]
                })
        
        return result
    
    except Exception as e:
        return {
            "file": file_path,
            "error": str(e),
            "functions": [],
            "classes": [],
            "imports": []
        }


def build_call_graph(parsed_files: List[Dict]) -> Dict:
    """Build a call graph from parsed files"""
    call_graph = {}
    
    # First pass: collect all functions and classes
    all_entities = {}
    for file_data in parsed_files:
        for func in file_data.get("functions", []):
            all_entities[func["name"]] = {
                "type": "function",
                "file": file_data["file"],
                "line": func["line_start"]
            }
        for cls in file_data.get("classes", []):
            all_entities[cls["name"]] = {
                "type": "class",
                "file": file_data["file"],
                "line": cls["line_start"]
            }
    
    # Second pass: find relationships
    for file_data in parsed_files:
        try:
            with open(file_data["file"], 'r', encoding='utf-8') as f:
                content = f.read()
            
            for func in file_data.get("functions", []):
                calls = []
                # Simple regex to find function calls
                for entity_name in all_entities:
                    if re.search(rf'\b{entity_name}\s*\(', content):
                        calls.append(entity_name)
                
                call_graph[func["name"]] = {
                    "calls": list(set(calls)),
                    "file": file_data["file"]
                }
        except Exception:
            continue
    
    return call_graph


# ============================================
# JAC CODE PARSING (Basic)
# ============================================

def parse_jac_file(file_path: str) -> Dict:
    """Basic parsing of Jac files using regex"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = {
            "file": file_path,
            "nodes": [],
            "walkers": [],
            "abilities": []
        }
        
        # Find nodes
        node_pattern = r'node\s+(\w+)\s*{'
        for match in re.finditer(node_pattern, content):
            result["nodes"].append(match.group(1))
        
        # Find walkers
        walker_pattern = r'walker\s+(\w+)\s*{'
        for match in re.finditer(walker_pattern, content):
            result["walkers"].append(match.group(1))
        
        # Find abilities
        ability_pattern = r'can\s+(\w+)'
        for match in re.finditer(ability_pattern, content):
            result["abilities"].append(match.group(1))
        
        return result
    
    except Exception as e:
        return {
            "file": file_path,
            "error": str(e),
            "nodes": [],
            "walkers": [],
            "abilities": []
        }


# ============================================
# MERMAID DIAGRAM GENERATION
# ============================================

def generate_class_diagram(parsed_files: List[Dict]) -> str:
    """Generate Mermaid class diagram"""
    lines = ["```mermaid", "classDiagram"]
    
    for file_data in parsed_files[:10]:  # Limit to first 10 files
        for cls in file_data.get("classes", []):
            class_name = cls["name"]
            lines.append(f"    class {class_name} {{")
            
            # Add methods
            for method in cls.get("methods", [])[:5]:  # Limit methods
                lines.append(f"        +{method}()")
            
            lines.append("    }")
            
            # Add inheritance
            for base in cls.get("bases", []):
                if base != "object":
                    lines.append(f"    {base} <|-- {class_name}")
    
    lines.append("```")
    return "\n".join(lines)


def generate_call_graph_diagram(call_graph: Dict) -> str:
    """Generate Mermaid flowchart for function calls"""
    lines = ["```mermaid", "graph TD"]
    
    # Limit to most connected functions
    sorted_funcs = sorted(call_graph.items(), key=lambda x: len(x[1].get("calls", [])), reverse=True)[:15]
    
    for func_name, data in sorted_funcs:
        for called_func in data.get("calls", [])[:5]:  # Limit calls per function
            if called_func in call_graph:
                lines.append(f"    {func_name} --> {called_func}")
    
    lines.append("```")
    return "\n".join(lines)


# ============================================
# DOCUMENTATION HELPERS
# ============================================

def get_current_datetime() -> str:
    """Get current datetime as string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def summarize_text(text: str, max_length: int = 500) -> str:
    """Simple text summarization"""
    if len(text) <= max_length:
        return text
    
    # Take first few paragraphs
    paragraphs = text.split('\n\n')
    summary = []
    current_length = 0
    
    for para in paragraphs:
        if current_length + len(para) > max_length:
            break
        summary.append(para)
        current_length += len(para)
    
    return '\n\n'.join(summary) + "..."


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
