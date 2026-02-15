#!/usr/bin/env python3
import os
import re
import sys
import requests
from packaging.version import parse as parse_version, InvalidVersion

# Regex for Dockerfile FROM instruction
# FROM image:tag AS ...
DOCKERFILE_FROM_RE = re.compile(r'^(FROM\s+)([^:\s]+):([a-zA-Z0-9.\-_]+)(\s+AS.*)?$', re.IGNORECASE)

# Regex for Compose image instruction
# image: image:tag
COMPOSE_IMAGE_RE = re.compile(r'^(\s*image:\s+)([^:\s]+):([a-zA-Z0-9.\-_]+)(\s*)$')
# image: image:${VAR:-tag}
COMPOSE_VAR_RE = re.compile(r'^(\s*image:\s+)([^:\s]+):\$\{([A-Z0-9_]+):-([a-zA-Z0-9.\-_]+)\}(\s*)$')


def get_docker_tags(image_name):
    """
    Get list of tags for an image from Docker Hub.
    Handles official images (library/image) and user images (user/image).
    """
    if '/' not in image_name:
        image_name = f"library/{image_name}"
    
    url = f"https://hub.docker.com/v2/repositories/{image_name}/tags/?page_size=100"
    tags = []
    
    try:
        while url:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                print(f"Failed to fetch tags for {image_name}: {resp.status_code}")
                return []
                
            data = resp.json()
            results = data.get('results', [])
            for r in results:
                tags.append(r['name'])
                
            url = data.get('next')
            # Limit to first page for now to avoid too many requests and limit finding potentially *too old* versions if we sort semantic
            # Actually, Hub returns latest pushed first usually.
            if len(tags) >= 100:
                break
    except Exception as e:
        print(f"Error fetching tags for {image_name}: {e}")
        return []
        
    return tags

def get_newer_version(current_tag, available_tags):
    """
    Find the newest version in available_tags that is greater than current_tag
    and matches the same suffix pattern (e.g. -alpine).
    """
    # 1. Identify suffix content (e.g. -alpine, -slim, or nothing)
    # We assume distinct parts separated by '-'.
    # If version is 1.2.3-alpine, version part is 1.2.3, suffix is -alpine.
    
    version_part = current_tag
    suffix = ""
    
    # Heuristic: split by first hyphen if it looks like a version number
    match = re.match(r'^([0-9]+\.[0-9]+(?:\.[0-9]+)?)(.*)$', current_tag)
    if match:
        version_part = match.group(1)
        suffix = match.group(2)
    else:
        # Check for simple integer versions like '15-alpine'
        match_int = re.match(r'^([0-9]+)(.*)$', current_tag)
        if match_int:
            version_part = match_int.group(1)
            suffix = match_int.group(2)
        else:
            return None # Cannot parse version structure
            
    try:
        current_ver = parse_version(version_part)
    except InvalidVersion:
        return None

    best_ver = current_ver
    best_tag = None

    for tag in available_tags:
        # Must match suffix
        if not tag.endswith(suffix):
            continue
            
        # Extract version part from tag
        # It must match the structure: version_part + suffix
        # e.g. if suffix is -alpine, tag must be Something-alpine.
        # And Something must be a valid version.
        
        tag_version_str = tag[:-len(suffix)] if suffix else tag
        
        # Avoid matching completely different tags that happen to end with same suffix
        # e.g. 'latest-alpine' vs '3.19-alpine'.
        # We only want numeric versions.
        if not re.match(r'^[0-9]+\.[0-9]+(?:\.[0-9]+)?$', tag_version_str) and not re.match(r'^[0-9]+$', tag_version_str):
             continue

        try:
            tag_ver = parse_version(tag_version_str)
            if tag_ver > best_ver and not tag_ver.is_prerelease:
                best_ver = tag_ver
                best_tag = tag
        except InvalidVersion:
            continue
            
    return best_tag

def process_file(filepath):
    print(f"Scanning {filepath}...")
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    new_lines = []
    changed = False
    
    for line in lines:
        # Check Dockerfile
        m_docker = DOCKERFILE_FROM_RE.match(line)
        m_compose = COMPOSE_IMAGE_RE.match(line)
        m_compose_var = COMPOSE_VAR_RE.match(line)
        
        replacement = None
        
        if m_docker:
            prefix, image, tag, suffix = m_docker.groups()
            tags = get_docker_tags(image)
            newer = get_newer_version(tag, tags)
            if newer:
                print(f"  {image}: {tag} -> {newer}")
                replacement = f"{prefix}{image}:{newer}{suffix or ''}\n"
                
        elif m_compose:
            prefix, image, tag, suffix = m_compose.groups()
            tags = get_docker_tags(image)
            newer = get_newer_version(tag, tags)
            if newer:
                print(f"  {image}: {tag} -> {newer}")
                replacement = f"{prefix}{image}:{newer}{suffix}\n"
                
        elif m_compose_var:
            prefix, image, var_name, tag, suffix = m_compose_var.groups()
            tags = get_docker_tags(image)
            newer = get_newer_version(tag, tags)
            if newer:
                print(f"  {image}: {tag} -> {newer} (in var {var_name})")
                replacement = f"{prefix}{image}:${{{var_name}:-{newer}}}{suffix}\n"

        if replacement:
            new_lines.append(replacement)
            changed = True
        else:
            new_lines.append(line)
            
    if changed:
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        print(f"Updated {filepath}")

def main():
    if len(sys.argv) < 2:
        print("Usage: update_docker_images.py [directory]")
        sys.exit(1)
        
    root_dir = sys.argv[1]
    
    for root, dirs, files in os.walk(root_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        if ".venv" in dirs:
            dirs.remove(".venv")
            
        for file in files:
            if file == "Dockerfile" or file == "compose.yaml" or file == "compose.yml":
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
