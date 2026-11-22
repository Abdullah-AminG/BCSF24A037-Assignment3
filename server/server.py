import os

from fastmcp import FastMCP

from tools import (
    marks_to_grade_points,
    calculate_semester_gpa,
    calculate_new_cgpa,
    required_gpa_for_target,
    get_semester_courses,
    get_remaining_credit_hours,
)

mcp = FastMCP("cgpa")

# Turn each plain function into an MCP tool.
# (docstring + type hints = the description the model reads)
for fn in (marks_to_grade_points, calculate_semester_gpa, calculate_new_cgpa,
           required_gpa_for_target, get_semester_courses, get_remaining_credit_hours):
    mcp.tool(fn)

if __name__ == "__main__":
    # Local:  http://127.0.0.1:8000/mcp
    # Hosted: Render gives PORT and needs HOST=0.0.0.0
    mcp.run(
        transport="http",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
    )
