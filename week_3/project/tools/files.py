"""
Sandboxed file tools — see week_3/2_agent_class.md
"""

import os
import glob as glob_module


WORKSPACE_ROOT = os.path.abspath(os.environ.get("WORKSPACE_ROOT", "."))

def resolve_path(path: str) -> str:
    """Security Guard: Ensure the AI cannot escape the workspace."""
    abs_path = os.path.abspath(os.path.join(WORKSPACE_ROOT, path))
    if not abs_path.startswith(WORKSPACE_ROOT):
        raise ValueError(f"Security violation: path {abs_path} is outside workspace.")
    return abs_path

def read_file(path: str, start_line: int = 1, read_lines: int = 200) -> dict:
    """Read a specific chunk of lines, adding line numbers for the AI to see."""
    try:
        safe_path = resolve_path(path)
        if not os.path.exists(safe_path):
            return {"error": f"File not found: {path}"}
            
        with open(safe_path, 'r') as f:
            lines = f.readlines()
            
        total_lines = len(lines)
        start_idx = max(0, start_line - 1)
        end_idx = min(start_idx + read_lines, total_lines)
        
        
        numbered_lines = []
        for i in range(start_idx, end_idx):
            line_num = i + 1
            numbered_lines.append(f"{line_num:4d} | {lines[i]}")
            
        chunk = "".join(numbered_lines)
        has_more = end_idx < total_lines
        
        return {
            "content": chunk, 
            "start_line": start_line, 
            "end_line": end_idx, 
            "total_lines": total_lines, 
            "has_more": has_more
        }
    except Exception as e:
        return {"error": str(e)}

def write_file(path: str, content: str) -> dict:
    """Create or completely overwrite a file."""
    try:
        safe_path = resolve_path(path)
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        with open(safe_path, 'w') as f:
            f.write(content)
        return {"success": True, "path": path, "bytes": len(content)}
    except Exception as e:
        return {"error": str(e)}

def edit_file(path: str, operation: str, start_line: int, end_line: int | None = None, content: str | None = None) -> dict:
    """Advanced: Replace, delete, or append specific lines in an existing file."""
    try:
        safe_path = resolve_path(path)
        if not os.path.exists(safe_path):
            return {"error": f"File not found: {path}"}
            
        with open(safe_path, 'r') as f:
            lines = f.readlines()
            
        start_idx = max(0, start_line - 1)
        end_idx = max(0, end_line if end_line is not None else start_line)
        
        new_lines = content.splitlines(True) if content else []
        # Ensure the last line has a line break
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines[-1] += '\n'

        if operation == "replace":
            lines[start_idx:end_idx] = new_lines
        elif operation == "delete":
            del lines[start_idx:end_idx]
        elif operation == "append":
            # Appends the new code exactly at the starting line
            lines[start_idx:start_idx] = new_lines
        else:
            return {"error": f"Unknown operation: {operation}. Use replace, delete, or append."}

        with open(safe_path, 'w') as f:
            f.writelines(lines)
            
        return {"success": True, "operation": operation, "affected_lines": f"{start_line}-{end_line}"}
    except Exception as e:
        return {"error": str(e)}

def list_files(path: str = ".", pattern: str = "*") -> dict:
    """List files in the workspace matching a pattern."""
    try:
        safe_path = resolve_path(path)
        search_pattern = os.path.join(safe_path, "**", pattern)
        files = glob_module.glob(search_pattern, recursive=True)
        
        relative_files = [os.path.relpath(f, WORKSPACE_ROOT) for f in files if os.path.isfile(f)]
        return {"files": relative_files}
    except Exception as e:
        return {"error": str(e)}