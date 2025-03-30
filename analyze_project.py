#!/usr/bin/env python3
"""
AI Tutor Project Analyzer

This script analyzes an AI Tutor project directory, determines the current progress,
identifies errors, and generates recommendations for next steps.
"""

import os
import json
import re
import argparse
import glob
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional

class ProjectAnalyzer:
    """Analyzes an AI Tutor project directory structure and files."""
    
    # Define expected project components
    EXPECTED_COMPONENTS = {
        "curriculum": ["curriculum_structure.json", "learning_paths.json"],
        "backend": ["main.py", "requirements.txt", "models.py", "database.py", "routers"],
        "frontend": ["package.json", "src", "public"],
        "ai_models": ["model_config.json", "fine_tuning", "prompts"],
        "voice": ["stt_config.json", "tts_config.json"],
        "agents": ["agent_config.json", "workflows"],
        "deployment": ["Dockerfile", "docker-compose.yml", "k8s"]
    }
    
    # Mapping of file extensions to programming languages
    FILE_TYPES = {
        ".py": "Python",
        ".js": "JavaScript",
        ".jsx": "React",
        ".ts": "TypeScript",
        ".tsx": "React/TypeScript",
        ".json": "JSON",
        ".html": "HTML",
        ".css": "CSS",
        ".md": "Markdown",
        ".yml": "YAML",
        ".yaml": "YAML",
        ".sql": "SQL"
    }
    
    def __init__(self, project_root: str):
        """Initialize with the project root directory."""
        self.project_root = os.path.abspath(project_root)
        self.files = []
        self.component_status = {}
        self.errors = []
        self.file_counts = defaultdict(int)
        self.code_analysis = {}
        
    def scan_directory(self) -> None:
        """Scan the project directory recursively."""
        print(f"Scanning project directory: {self.project_root}")
        
        # Check if directory exists
        if not os.path.isdir(self.project_root):
            raise ValueError(f"Project directory does not exist: {self.project_root}")
        
        # Recursively find all files
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.startswith('.') or '__pycache__' in root:
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_root)
                
                # Get file extension
                _, ext = os.path.splitext(file)
                
                # Add to file list
                self.files.append({
                    "path": rel_path,
                    "type": self.FILE_TYPES.get(ext, "Unknown"),
                    "size": os.path.getsize(file_path)
                })
                
                # Update file type counts
                self.file_counts[self.FILE_TYPES.get(ext, "Unknown")] += 1
        
        print(f"Found {len(self.files)} files in the project.")

    def analyze_component_status(self) -> None:
        """Analyze the status of each expected component."""
        print("Analyzing component status...")
        
        # Convert files list to a set of paths for faster lookup
        file_paths = {file["path"] for file in self.files}
        
        for component, expected_files in self.EXPECTED_COMPONENTS.items():
            found_files = []
            missing_files = []
            
            for expected in expected_files:
                # Check if the expected file/directory exists
                matches = False
                for path in file_paths:
                    # Check for exact match or directory match
                    if path == expected or path.startswith(f"{expected}/"):
                        matches = True
                        found_files.append(path)
                
                if not matches:
                    missing_files.append(expected)
            
            # Calculate component completion percentage
            total_expected = len(expected_files)
            total_found = total_expected - len(missing_files)
            completion_pct = (total_found / total_expected * 100) if total_expected > 0 else 0
            
            self.component_status[component] = {
                "status": "Complete" if completion_pct == 100 else "In Progress" if completion_pct > 0 else "Not Started",
                "completion_percentage": completion_pct,
                "found_files": found_files,
                "missing_files": missing_files
            }

    def find_errors(self) -> None:
        """Identify potential errors in the codebase."""
        print("Scanning for potential errors...")
        
        for file_info in self.files:
            file_path = os.path.join(self.project_root, file_info["path"])
            file_type = file_info["type"]
            
            # Skip non-text files or large files
            if file_info["size"] > 1000000 or file_type == "Unknown":
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Look for common error patterns based on file type
                    if file_type == "Python":
                        # Check for imports with no requirements
                        imports = re.findall(r'import\s+(\w+)', content)
                        
                        # Check for TODO comments
                        todos = re.findall(r'#\s*TODO', content)
                        if todos:
                            self.errors.append({
                                "file": file_info["path"],
                                "type": "TODO",
                                "message": f"Found {len(todos)} TODO comments"
                            })
                            
                        # Check for exception handling
                        except_blocks = re.findall(r'except\s+\w+\s*:', content)
                        bare_excepts = re.findall(r'except\s*:', content)
                        if bare_excepts:
                            self.errors.append({
                                "file": file_info["path"],
                                "type": "Code Quality",
                                "message": "Found bare except clause - should specify exception type"
                            })
                            
                    elif file_type in ["JavaScript", "TypeScript", "React", "React/TypeScript"]:
                        # Check for console.log statements
                        console_logs = re.findall(r'console\.log', content)
                        if console_logs:
                            self.errors.append({
                                "file": file_info["path"],
                                "type": "Development Code",
                                "message": f"Found {len(console_logs)} console.log statements"
                            })
                            
                        # Check for TODO comments
                        todos = re.findall(r'//\s*TODO', content)
                        if todos:
                            self.errors.append({
                                "file": file_info["path"],
                                "type": "TODO",
                                "message": f"Found {len(todos)} TODO comments"
                            })
                            
                    # Check for environment variables hardcoded
                    api_keys = re.findall(r'(api[_-]?key|secret|password|token)\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
                    if api_keys:
                        self.errors.append({
                            "file": file_info["path"],
                            "type": "Security",
                            "message": f"Potential hardcoded credentials found"
                        })
                            
            except Exception as e:
                self.errors.append({
                    "file": file_info["path"],
                    "type": "Analysis Error",
                    "message": f"Could not analyze file: {str(e)}"
                })

    def analyze_code_structure(self) -> None:
        """Analyze the structure of the code."""
        print("Analyzing code structure...")
        
        # Check for backend frameworks
        backend_frameworks = {
            "fastapi": False,
            "flask": False,
            "django": False,
        }
        
        # Check for database related code
        database_technologies = {
            "sqlalchemy": False,
            "postgresql": False,
            "mongodb": False,
        }
        
        # Check for AI libraries
        ai_libraries = {
            "langchain": False,
            "autogen": False,
            "crewai": False,
            "openai": False,
            "anthropic": False,
        }
        
        # Find requirements.txt or package.json
        req_files = [f for f in self.files if f["path"].endswith(("requirements.txt", "package.json"))]
        
        for file_info in req_files:
            file_path = os.path.join(self.project_root, file_info["path"])
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    if file_path.endswith("requirements.txt"):
                        # Check for Python packages
                        for framework in backend_frameworks:
                            if re.search(rf'{framework}[=~><]', content, re.IGNORECASE):
                                backend_frameworks[framework] = True
                                
                        for db in database_technologies:
                            if re.search(rf'{db}[=~><]', content, re.IGNORECASE):
                                database_technologies[db] = True
                                
                        for lib in ai_libraries:
                            if re.search(rf'{lib}[=~><]', content, re.IGNORECASE):
                                ai_libraries[lib] = True
                    
                    elif file_path.endswith("package.json"):
                        # Parse package.json
                        try:
                            package_data = json.loads(content)
                            dependencies = {**package_data.get("dependencies", {}), **package_data.get("devDependencies", {})}
                            
                            # Check for frontend frameworks
                            has_react = "react" in dependencies
                            has_nextjs = "next" in dependencies
                            
                            self.code_analysis["frontend_framework"] = "React" if has_react else "Next.js" if has_nextjs else "Unknown"
                            
                        except json.JSONDecodeError:
                            self.errors.append({
                                "file": file_info["path"],
                                "type": "Parse Error",
                                "message": "Invalid JSON in package.json"
                            })
            except Exception as e:
                self.errors.append({
                    "file": file_info["path"],
                    "type": "Analysis Error",
                    "message": f"Could not analyze file: {str(e)}"
                })
        
        # Store the results
        self.code_analysis["backend_framework"] = next((k for k, v in backend_frameworks.items() if v), "Unknown")
        self.code_analysis["database_technology"] = next((k for k, v in database_technologies.items() if v), "Unknown")
        self.code_analysis["ai_libraries"] = [k for k, v in ai_libraries.items() if v]

    def generate_next_steps(self) -> Dict:
        """Generate recommendations for next steps based on analysis."""
        print("Generating next steps recommendations...")
        
        # Determine the least developed components
        least_developed = sorted(
            self.component_status.items(), 
            key=lambda x: x[1]["completion_percentage"]
        )
        
        next_steps = {
            "priority_components": [],
            "recommended_tasks": [],
            "claude_prompt": ""
        }
        
        # Add top 3 least developed components
        for component, status in least_developed[:3]:
            if status["completion_percentage"] < 100:
                next_steps["priority_components"].append({
                    "component": component,
                    "status": status["status"],
                    "completion": f"{status['completion_percentage']:.1f}%"
                })
                
                # Add specific tasks based on missing files
                for missing in status["missing_files"][:3]:  # Limit to 3 missing files
                    next_steps["recommended_tasks"].append(f"Create {component}/{missing}")
        
        # Add error fixes
        for error in self.errors[:5]:  # Limit to 5 errors
            next_steps["recommended_tasks"].append(
                f"Fix {error['type']} in {error['file']}: {error['message']}"
            )
            
        # Create Claude prompt
        claude_prompt = self._generate_claude_prompt(next_steps["priority_components"], next_steps["recommended_tasks"])
        next_steps["claude_prompt"] = claude_prompt
        
        return next_steps
    
    def _generate_claude_prompt(self, priority_components, recommended_tasks) -> str:
        """Generate a prompt for Claude to continue development."""
        
        # Start with the project overview
        prompt = "# AI Tutor Project: Next Development Steps\n\n"
        
        # Add project status summary
        total_components = len(self.component_status)
        completed = sum(1 for status in self.component_status.values() if status["status"] == "Complete")
        in_progress = sum(1 for status in self.component_status.values() if status["status"] == "In Progress")
        not_started = sum(1 for status in self.component_status.values() if status["status"] == "Not Started")
        
        prompt += f"## Project Status\n"
        prompt += f"- Total Components: {total_components}\n"
        prompt += f"- Complete: {completed}\n"
        prompt += f"- In Progress: {in_progress}\n"
        prompt += f"- Not Started: {not_started}\n\n"
        
        # Add technology stack information
        prompt += f"## Current Technology Stack\n"
        prompt += f"- Backend: {self.code_analysis.get('backend_framework', 'Unknown')}\n"
        prompt += f"- Database: {self.code_analysis.get('database_technology', 'Unknown')}\n"
        prompt += f"- Frontend: {self.code_analysis.get('frontend_framework', 'Unknown')}\n"
        prompt += f"- AI Libraries: {', '.join(self.code_analysis.get('ai_libraries', ['None detected']))}\n\n"
        
        # Add priority components section
        prompt += "## Priority Components\n"
        for component in priority_components:
            prompt += f"- {component['component']} ({component['completion']} complete)\n"
        prompt += "\n"
        
        # Add recommended tasks
        prompt += "## Recommended Tasks\n"
        for i, task in enumerate(recommended_tasks, 1):
            prompt += f"{i}. {task}\n"
        prompt += "\n"
        
        # Add specific request to Claude
        prompt += "## Request\n"
        if priority_components:
            top_priority = priority_components[0]['component']
            prompt += f"Please help me develop the {top_priority} component of my AI Tutor project. "
            prompt += f"Based on the project analysis, this is the highest priority area that needs attention.\n\n"
            prompt += f"Specifically, I need help with:\n"
            
            # Extract tasks related to the top priority
            related_tasks = [task for task in recommended_tasks if top_priority in task]
            for task in related_tasks[:3]:
                prompt += f"- {task}\n"
                
            prompt += "\nPlease provide detailed implementation guidance, code samples, and explanations for how to make progress on these tasks."
        else:
            prompt += "Please help me make progress on my AI Tutor project. Based on the analysis, suggest implementation details for the next logical steps."
            
        return prompt

    def run_analysis(self) -> Dict:
        """Run the complete analysis and return results."""
        self.scan_directory()
        self.analyze_component_status()
        self.find_errors()
        self.analyze_code_structure()
        next_steps = self.generate_next_steps()
        
        # Prepare the full analysis results
        results = {
            "project_root": self.project_root,
            "file_count": len(self.files),
            "file_types": dict(self.file_counts),
            "component_status": self.component_status,
            "errors": self.errors,
            "code_analysis": self.code_analysis,
            "next_steps": next_steps
        }
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Analyze AI Tutor project and generate next steps')
    parser.add_argument('--project-dir', '-p', type=str, default='.', 
                        help='Path to the AI Tutor project directory (default: current directory)')
    parser.add_argument('--output', '-o', type=str, default='ai_tutor_analysis.json',
                        help='Output file for the analysis results (default: ai_tutor_analysis.json)')
    args = parser.parse_args()
    
    try:
        analyzer = ProjectAnalyzer(args.project_dir)
        results = analyzer.run_analysis()
        
        # Print summary to console
        print("\n" + "="*50)
        print("AI TUTOR PROJECT ANALYSIS SUMMARY")
        print("="*50)
        print(f"Project directory: {results['project_root']}")
        print(f"Total files: {results['file_count']}")
        
        print("\nComponent Status:")
        for component, status in results['component_status'].items():
            print(f"- {component}: {status['status']} ({status['completion_percentage']:.1f}%)")
        
        print("\nDetected Errors:")
        for error in results['errors'][:5]:  # Show top 5 errors
            print(f"- {error['file']}: {error['type']} - {error['message']}")
            
        print("\nPriority Components:")
        for component in results['next_steps']['priority_components']:
            print(f"- {component['component']} ({component['completion']})")
            
        print("\nRecommended Tasks:")
        for task in results['next_steps']['recommended_tasks']:
            print(f"- {task}")
            
        # Save full results to file
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
            
        print(f"\nFull analysis saved to {args.output}")
        print(f"\nClaude prompt ready! You can copy it from the results file or the 'claude_prompt' field.")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())