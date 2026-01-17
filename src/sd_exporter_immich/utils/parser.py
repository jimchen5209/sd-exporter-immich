def _remove_lora_tags_string(text: str) -> str:
    result: list[str] = []
    current_pos = 0

    while current_pos < len(text):
        lora_start = text.find("<lora:", current_pos)

        if lora_start == -1:
            result.append(text[current_pos:])  # Append remaining text
            break

        # Append text before the found <lora:
        result.append(text[current_pos:lora_start])

        lora_end = text.find(">", lora_start)

        if lora_end == -1:
            # If <lora: is found but no closing >, treat the rest as regular text
            result.append(text[lora_start:])
            break

        # If a complete <lora:...> tag is found, skip it
        current_pos = lora_end + 1

    return "".join(result)


def _remove_scheduling(text: str):
    """
    Remove scheduling pattern [x:x:number] and extract value
    """
    result: list[str] = []
    extracted_pairs: list[tuple[str, str]] = []
    i = 0

    while i < len(text):
        # Check escaped [
        if i > 0 and text[i - 1 : i + 1] == r"\[":
            result.append(text[i])
            i += 1
            continue

        # find [
        if text[i] == "[":
            bracket_start = i
            i += 1

            # find first :
            first_colon = -1
            while i < len(text) and text[i] not in "[]":
                if text[i] == ":" and first_colon == -1:
                    first_colon = i
                    break
                i += 1

            if first_colon == -1:
                # Not a scheduling pattern, restore
                result.append(text[bracket_start])
                i = bracket_start + 1
                continue

            # Extract first tag
            tag1 = text[bracket_start + 1 : first_colon]
            i = first_colon + 1

            # Find second :
            second_colon = -1
            while i < len(text) and text[i] not in "[]":
                if text[i] == ":" and second_colon == -1:
                    second_colon = i
                    break
                i += 1

            if second_colon == -1:
                # Not a scheduling pattern, restore
                result.append(text[bracket_start])
                i = bracket_start + 1
                continue

            # Extract Second tag
            tag2 = text[first_colon + 1 : second_colon]
            i = second_colon + 1

            # Find number and find ]
            number_start = i
            while i < len(text) and text[i] not in "[]":
                i += 1

            if i >= len(text) or text[i] != "]":
                # Not a scheduling pattern, restore
                result.append(text[bracket_start])
                i = bracket_start + 1
                continue

            # Verify if it's a valid
            number_str = text[number_start:i]
            try:
                _ = float(number_str)
                # 是有效的 scheduling pattern
                extracted_pairs.append((tag1.strip(), tag2.strip()))
                i += 1  # Skip ]
            except ValueError:
                # Not a valid number, restore
                result.append(text[bracket_start])
                i = bracket_start + 1
        else:
            result.append(text[i])
            i += 1

    return "".join(result), extracted_pairs


def _remove_de_emphasis(text: str, open_char: str = "[", close_char: str = "]"):
    """
    Remove de-emphasis [x] (Not escaped)
    """
    result: list[str] = []
    i = 0

    while i < len(text):
        # Check escaped brackets
        if i > 0 and text[i - 1] == "\\" and text[i] in [open_char, close_char]:
            result.append(text[i])
            i += 1
            continue

        # Find open (
        if text[i] == open_char:
            # Find corresponding close bracket
            depth = 1
            j = i + 1
            content_start = j

            while j < len(text) and depth > 0:
                # Skip escaped
                if j > 0 and text[j - 1] == "\\":
                    j += 1
                    continue

                if text[j] == open_char:
                    depth += 1
                elif text[j] == close_char:
                    depth -= 1
                j += 1

            if depth == 0:
                # Found brackets, extract content
                content = text[content_start : j - 1]
                result.append(content)
                i = j
                continue

        result.append(text[i])
        i += 1

    return "".join(result)


def _remove_emphasis_with_multiply(text: str):
    """
    Remove emphasis (x) (Not escaped)
    Remove Multiply emphasis (x:number) (Not escaped)
    """
    result: list[str] = []
    i = 0

    while i < len(text):
        # Check escaped
        if i > 0 and text[i - 1] == "\\" and text[i] == "(":
            result.append(text[i])
            i += 1
            continue

        # Find open bracket
        if text[i] == "(":
            # Find corresponding close bracket
            j = i + 1
            while j < len(text) and text[j] != ")":
                # Skip escaped bracket
                if j > 0 and text[j - 1] == "\\":
                    j += 1
                    continue
                j += 1

            if j < len(text) and text[j] == ")":
                # Extract content
                content = text[i + 1 : j]

                # Check if x:number
                colon_pos = content.find(":")
                if colon_pos != -1:
                    tag_part = content[:colon_pos]
                    number_part = content[colon_pos + 1 :]

                    # Verify number
                    try:
                        _ = float(number_part.strip())
                        # is (x:number) , keep x
                        result.append(tag_part)
                        i = j + 1
                        continue
                    except ValueError:
                        pass

                # normal (x) , keep content
                result.append(content)
                i = j + 1
                continue

        result.append(text[i])
        i += 1

    return "".join(result)


def _remove_multiply_suffix(text: str):
    """
    Remove Multiply x:number
    """
    result: list[str] = []
    words = text.split()

    for word in words:
        # Find if end with comma
        has_comma = word.endswith(",")
        if has_comma:
            word = word[:-1]

        # Find last colon
        colon_pos = word.rfind(":")

        if colon_pos != -1:
            tag_part = word[:colon_pos]
            number_part = word[colon_pos + 1 :]

            # Verify number
            try:
                _ = float(number_part)
                # is x:number , keep x
                result.append(tag_part + ("," if has_comma else ""))
            except ValueError:
                # Not a number, keep original
                result.append(word + ("," if has_comma else ""))
        else:
            # No colon, keep original
            result.append(word + ("," if has_comma else ""))

    return " ".join(result)


def _parse_settings(text: str):
    """
    Parse: key: value, key: value
    """
    settings: dict[str, str] = {}
    i = 0

    while i < len(text):
        # Skip space
        while i < len(text) and text[i].isspace():
            i += 1

        if i >= len(text):
            break

        # Read key (Until colon)
        key_start = i
        while i < len(text) and text[i] not in ":,":
            i += 1

        if i >= len(text) or text[i] != ":":
            # No colon, skip
            while i < len(text) and text[i] != ",":
                i += 1
            if i < len(text):
                i += 1  # Skip comma
            continue

        key = text[key_start:i].strip()
        i += 1  # Skip colon

        # Skip space
        while i < len(text) and text[i].isspace():
            i += 1

        if i >= len(text):
            break

        # Read value
        value_start = i

        # Check is covered with quote
        if text[i] == '"':
            i += 1  # Skip quote start
            value_content_start = i

            # Find ending quote
            while i < len(text):
                if text[i] == "\\" and i + 1 < len(text):
                    # Skip escaped
                    i += 2
                    continue
                elif text[i] == '"':
                    # Found ending quote
                    value = text[value_content_start:i]
                    i += 1  # Skip ending quote
                    break
                i += 1
            else:
                # No ending quote, take to the end
                value = text[value_content_start:]
        else:
            # Not a quote, read to comma or the end
            while i < len(text) and text[i] != ",":
                i += 1
            value = text[value_start:i].strip()

        settings[key] = value

        # Skip comma
        while i < len(text) and text[i] in ", \t":
            i += 1

    return settings


def parse_tag(prompt: str) -> list[str]:
    """
    Parse prompt according to Native Prompt Parser format on sdnext, remove modifiers and extract tags
    """
    if not prompt or not isinstance(prompt, str):  # pyright: ignore[reportUnnecessaryIsInstance] prevent runtime error
        return []

    parts = prompt.split(",")

    cleaned_tags: list[str] = []

    for part in parts:
        # Remove LoRA parts
        part = _remove_lora_tags_string(part).strip()

        # Pass if part is empty after removing LoRA parts
        if not part:
            continue

        # Process prompt scheduling [x:x:number], taking two x
        part, pairs = _remove_scheduling(part)
        for tags in pairs:
            cleaned_tags.extend(tags)

        # Remove de-emphasis [x] (Not escaped)
        part = _remove_de_emphasis(part)

        # Remove emphasis (x) and multiply emphasis (x:number) (Not escaped)
        part = _remove_emphasis_with_multiply(part)

        # Remove Multiply x:number
        part = _remove_multiply_suffix(part)

        # Restore Escaped：\( -> (, \) -> ), \[ -> [, \] -> ], \{ -> {, \} -> }
        part = part.replace(r"\(", "(")
        part = part.replace(r"\)", ")")
        part = part.replace(r"\[", "[")
        part = part.replace(r"\]", "]")
        part = part.replace(r"\{", "{")
        part = part.replace(r"\}", "}")

        part = part.strip()
        if part:
            cleaned_tags.append(part)

    return cleaned_tags


def parse_settings(settings: str) -> dict[str, str]:
    """
    Convert a comma-separated key: value format string into a dictionary
    """
    parsed_settings = _parse_settings(settings)

    return parsed_settings
