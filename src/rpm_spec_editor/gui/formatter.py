SPEC_TAGS = {
    "Name",
    "Epoch",
    "Version",
    "Release",
    "Summary",
    "License",
    "URL",
    "Source0",
    "Source1",
    "BuildRequires",
    "Requires",
}


def align_spec_fields(text, min_spaces=2):
    lines = text.splitlines()

    parsed_lines = []
    longest_tag = 0

    for line in lines:
        stripped = line.strip()

        if (
            not stripped
            or stripped.startswith("%")
            or ":" not in line
        ):
            parsed_lines.append(("raw", line))
            continue

        key, value = line.split(":", 1)

        key = key.strip()

        if key not in SPEC_TAGS:
            parsed_lines.append(("raw", line))
            continue

        tag = key + ":"

        if len(tag) > longest_tag:
            longest_tag = len(tag)

        parsed_lines.append(("spec", (tag, value.strip())))

    result = []

    for line_type, data in parsed_lines:

        if line_type == "raw":
            result.append(data)
            continue

        tag, value = data

        spaces = " " * (longest_tag - len(tag) + min_spaces)

        formatted = f"{tag}{spaces}{value}"

        result.append(formatted)

    return "\n".join(result)