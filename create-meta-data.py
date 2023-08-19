import toml
import sys
import os

def extract_poetry_properties(project_file):
    try:
        # Load the pyproject.toml
        data = toml.load(project_file)

        # Extract the required properties
        poetry_data = data.get("tool", {}).get("poetry", {})
        
        name = poetry_data.get("name", "")
        version = poetry_data.get("version", "")
        description = poetry_data.get("description", "")
        authors = poetry_data.get("authors", [])
        license_ = poetry_data.get("license", "")
        
        return {
            "name": name,
            "version": version,
            "description": description,
            "authors": authors,
            "license": license_
        }
    except Exception as e:
        # Handle the exception if the file is not accessible or any other issue
        print(f"Error reading {project_file}: {e}")
        return {}

def write_metadata(properties, output_path):
    with open(os.path.join(output_path, "app_meta_data.py"), "w") as file:
        file.write("from dataclasses import dataclass, field\n\n")
        file.write("@dataclass\n")
        file.write("class AppMetaData:\n")
        file.write(f"    name: str = '{properties['name']}'\n")
        file.write(f"    version: str = '{properties['version']}'\n")
        file.write(f"    description: str = '''{properties['description']}'''\n")
        file.write("    authors: list = field(default_factory=lambda: " + f"{properties['authors']})\n")
        file.write(f"    license: str = '{properties['license']}'\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create-meta-data.py <project-file> <output-path>")
        sys.exit(1)
    
    project_file = sys.argv[1]
    output_path = sys.argv[2]

    properties = extract_poetry_properties(project_file)
    write_metadata(properties, output_path)
