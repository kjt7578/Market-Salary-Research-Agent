# config.py

TRUSTED_SOURCES = [
    "ZipRecruiter",
    "Salary.com",
    "Indeed",
    "Levels.fyi"
]

PROMPT_TEMPLATE = (
    "I want to know the average salary for a {role} with {experience_level} in {location}. "
    "Please answer ONLY based on the following sources: {sources}. "
    "Respond strictly in the following JSON format: "
    "{{\n"
    "  \"salary_range\": \"min - max\",\n"
    "  \"min\": int,\n"
    "  \"max\": int,\n"
    "  \"median\": int,\n"
    "  \"average\": int,\n"
    "  \"percentile_75\": int,\n"
    "  \"total_compensation\": int,\n"
    "  \"source_summary\": {{\"ZipRecruiter\": \"...\", ...}},\n"
    "  \"text_summary\": \"...\"\n"
    "}}\n"
    "If you cannot find a value, set it to null."
) 