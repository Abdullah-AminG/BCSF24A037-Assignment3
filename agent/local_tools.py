"""Tools that must run on the student's own machine (not on the MCP server)."""
from pathlib import Path


def save_report(filename: str, content: str) -> str:
    """Use ONLY when the student asks to save a finished GPA/CGPA report."""
    if (not isinstance(filename, str) or not filename.strip()
            or "/" in filename or "\\" in filename or filename in (".", "..")):
        return "Error: provide a simple filename"
    if not isinstance(content, str) or not content.strip():
        return "Error: report content cannot be empty"

    try:
        folder = Path("reports")
        folder.mkdir(exist_ok=True)
        with (folder / filename).open("x", encoding="utf-8") as file:
            file.write(content)
        return f"Report saved to {folder / filename}"
    except FileExistsError:
        return "Error: report already exists"
    except OSError:
        return "Error: report could not be saved"
