import re

def parse_tag(prompt: str) -> list[str]:
    """
    Parse prompt according to Native Prompt Parser format on sdnext, remove modifiers and extract tags
    """
    if not prompt or not isinstance(prompt, str):
        return []

    parts = prompt.split(',')
    
    cleaned_tags = []
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Process prompt scheduling [x:x:number], taking two x
        scheduling_match = re.search(r'(?<!\\)\[([^\[\]:]+?):([^\[\]:]+?):(\d+(?:\.\d+)?)\]', part)
        if scheduling_match:
            tag1 = scheduling_match.group(1).strip()
            tag2 = scheduling_match.group(2).strip()
            if tag1:
                cleaned_tags.append(tag1)
            if tag2:
                cleaned_tags.append(tag2)
            continue
        
        # Remove de-emphasis [x] (Not escaped)
        part = re.sub(r'(?<!\\)\[([^\[\]]+?)\]', r'\1', part)
        
        # Remove emphasis (x) (Not escaped)
        part = re.sub(r'(?<!\\)\(([^()]+?)\)', r'\1', part)
        
        # Remove Multiply emphasis (x:number) (Not escaped)
        part = re.sub(r'(?<!\\)\(([^():]+?):(\d+(?:\.\d+)?)\)', r'\1', part)
        
        # Remove Multiply x:number
        part = re.sub(r'(\S+?):(\d+(?:\.\d+)?)(?=\s|$|,)', r'\1', part)
        
        # Restore Escaped：\( -> (, \) -> ), \[ -> [, \] -> ], \{ -> {, \} -> }
        part = part.replace(r'\(', '(')
        part = part.replace(r'\)', ')')
        part = part.replace(r'\[', '[')
        part = part.replace(r'\]', ']')
        part = part.replace(r'\{', '{')
        part = part.replace(r'\}', '}')
        
        part = part.strip()
        if part:
            cleaned_tags.append(part)
    
    return cleaned_tags

def parse_settings(settings: str) -> dict[str, str]:
    """
    Convert a comma-separated key: value format string into a dictionary using regular expressions
    """
    result = {}
    
    # Regular expression description:
    # (\w+(?:\s+\w+)*) - Capture key (word character, can include spaces)
    # :\s* - matches colon and following space
    # (?:"([^"]*)"|([^,]+)) - Capture value (content within quotes or non-comma content)
    pattern = r'(\w+(?:\s+\w+)*):\s*(?:"([^"]*)"|([^,]+?))\s*(?:,|$)'
    
    matches = re.finditer(pattern, settings)
    
    for match in matches:
        key = match.group(1).strip()
        # group(2) is the value within quotes, group(3) is the value without quotes
        if match.group(2) is not None:
            value = match.group(2).strip()
        else:
            value = match.group(3).strip()
        
        result[key] = value
    
    return result
