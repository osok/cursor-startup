#!/usr/bin/env python3
import os
import ast
import argparse
import sys
from collections import Counter

# --------------------------------------------------
# AST Parsing for Classes (for UML generation)
# --------------------------------------------------

class UMLClassVisitor(ast.NodeVisitor):
    """
    Visits class definitions in a Python AST and collects:
      - Class-level and instance attributes.
      - Public and private methods, including parameter types and return types.
    """
    def __init__(self):
        self.classes = {}

    def visit_ClassDef(self, node):
        class_name = node.name
        attributes = set()
        private_attributes = set()
        methods = {}
        private_methods = {}

        # Process class-level attributes.
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        attr_name = target.id
                        if attr_name.startswith('_'):
                            private_attributes.add(attr_name)
                        else:
                            attributes.add(attr_name)
            elif isinstance(stmt, ast.AnnAssign):
                if isinstance(stmt.target, ast.Name):
                    attr_name = stmt.target.id
                    if attr_name.startswith('_'):
                        private_attributes.add(attr_name)
                    else:
                        attributes.add(attr_name)

        # Process methods and extract parameters/return types.
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                method_name = stmt.name

                # Skip magic methods.
                if method_name.startswith('__') and method_name.endswith('__'):
                    continue

                # Build parameter list with types (if available).
                param_list = []
                for arg in stmt.args.args:
                    if arg.arg == "self":
                        continue
                    if arg.annotation:
                        try:
                            annotation_str = ast.unparse(arg.annotation)
                        except Exception:
                            annotation_str = ""
                    else:
                        annotation_str = ""
                    if annotation_str:
                        param_list.append(f"{arg.arg}: {annotation_str}")
                    else:
                        param_list.append(arg.arg)

                # Extract return type if available.
                if stmt.returns:
                    try:
                        return_type = ast.unparse(stmt.returns)
                    except Exception:
                        return_type = ""
                else:
                    return_type = ""

                method_info = {
                    "params": param_list,
                    "return": return_type
                }

                if method_name.startswith('_'):
                    private_methods[method_name] = method_info
                else:
                    methods[method_name] = method_info

                # In __init__, capture instance attributes assigned to self.
                if method_name == '__init__':
                    for n in ast.walk(stmt):
                        if isinstance(n, ast.Assign):
                            for target in n.targets:
                                if isinstance(target, ast.Attribute):
                                    if (isinstance(target.value, ast.Name) and target.value.id == 'self'):
                                        attr_name = target.attr
                                        if attr_name.startswith('_'):
                                            private_attributes.add(attr_name)
                                        else:
                                            attributes.add(attr_name)

        self.classes[class_name] = {
            'attributes': sorted(list(attributes)),
            'private_attributes': sorted(list(private_attributes)),
            'methods': methods,
            'private_methods': private_methods
        }
        self.generic_visit(node)

def parse_python_file(filepath):
    """Parses one Python file and returns a dictionary of classes found."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            file_contents = f.read()
        tree = ast.parse(file_contents, filename=filepath)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return {}
    visitor = UMLClassVisitor()
    visitor.visit(tree)
    return visitor.classes

def compute_package_name(root_dir, current_dir):
    """
    Computes the package name from the current directory relative to the root.
    Files in the root are grouped under package 'root'.
    """
    rel_path = os.path.relpath(current_dir, root_dir)
    if rel_path == ".":
        return "root"
    return rel_path.replace(os.sep, ".")

def parse_directory(root_dir):
    """
    Walks the directory tree and parses all .py files for class definitions,
    grouping them by package.
    Instead of overwriting duplicate class names, each found class (with its module)
    is stored as an entry in a list.
    """
    packages = {}
    for dirpath, _, filenames in os.walk(root_dir):
        package_name = compute_package_name(root_dir, dirpath)
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                file_classes = parse_python_file(filepath)
                if file_classes:
                    if package_name not in packages:
                        packages[package_name] = []
                    module_name = os.path.splitext(filename)[0]
                    for class_name, data in file_classes.items():
                        packages[package_name].append({
                            "class_name": class_name,
                            "data": data,
                            "module": module_name
                        })
    return packages

def generate_plantuml(packages):
    """
    Generates PlantUML source text from the packages dictionary.
    For classes with duplicate names in the same package, the module name is appended.
    Method signatures include parameter types and return types if available.
    """
    uml_lines = [
        "@startuml",
        "skinparam pageMargin 50",
        "skinparam pageWidth 3000",
        "left to right direction",
        "direction LR"
    ]
    for pkg, class_entries in packages.items():
        uml_lines.append(f"package {pkg} {{")
        class_name_counts = Counter(entry["class_name"] for entry in class_entries)
        for entry in class_entries:
            orig_name = entry["class_name"]
            # Append module name if duplicate.
            if class_name_counts[orig_name] > 1:
                display_name = f"{orig_name} ({entry['module']})"
            else:
                display_name = orig_name
            data = entry["data"]
            uml_lines.append(f"  class {display_name} {{")
            for attr in data['attributes']:
                uml_lines.append(f"    + {attr}")
            for attr in data['private_attributes']:
                uml_lines.append(f"    - {attr}")
            for method, info in data['methods'].items():
                param_str = ", ".join(info["params"])
                if info["return"]:
                    uml_lines.append(f"    + {method}({param_str}) : {info['return']}")
                else:
                    uml_lines.append(f"    + {method}({param_str})")
            for method, info in data['private_methods'].items():
                param_str = ", ".join(info["params"])
                if info["return"]:
                    uml_lines.append(f"    - {method}({param_str}) : {info['return']}")
                else:
                    uml_lines.append(f"    - {method}({param_str})")
            uml_lines.append("  }")
        uml_lines.append("}")
    uml_lines.append("@enduml")
    return "\n".join(uml_lines)

# --------------------------------------------------
# AST Parsing for Module-Level Functions (including decorators)
# --------------------------------------------------

def parse_module_functions(filepath):
    """
    Parses a Python file and returns a dictionary of module-level functions found.
    Each function's details include parameters, return type, and decorators.
    """
    functions = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            file_contents = f.read()
        tree = ast.parse(file_contents, filename=filepath)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return functions

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            param_list = []
            for arg in node.args.args:
                if arg.annotation:
                    try:
                        annotation_str = ast.unparse(arg.annotation)
                    except Exception:
                        annotation_str = ""
                else:
                    annotation_str = ""
                if annotation_str:
                    param_list.append(f"{arg.arg}: {annotation_str}")
                else:
                    param_list.append(arg.arg)
            if node.returns:
                try:
                    return_type = ast.unparse(node.returns)
                except Exception:
                    return_type = ""
            else:
                return_type = ""
            # Extract decorators.
            decorators = []
            if node.decorator_list:
                for decorator in node.decorator_list:
                    try:
                        decorator_str = ast.unparse(decorator)
                    except Exception:
                        decorator_str = ""
                    if decorator_str:
                        decorators.append(decorator_str)
            functions[func_name] = {
                "params": param_list,
                "return": return_type,
                "decorators": decorators
            }
    return functions

def parse_directory_module_functions(root_dir):
    """
    Walks the directory tree and parses all .py files for module-level functions.
    Returns a dictionary mapping package names to a list of modules and their functions.
    """
    modules = {}
    for dirpath, _, filenames in os.walk(root_dir):
        package_name = compute_package_name(root_dir, dirpath)
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                funcs = parse_module_functions(filepath)
                if funcs:
                    if package_name not in modules:
                        modules[package_name] = []
                    module_name = os.path.splitext(filename)[0]
                    modules[package_name].append({
                        "module": module_name,
                        "functions": funcs
                    })
    return modules

def generate_module_functions_doc(modules):
    """
    Generates plain-text documentation of module-level functions.
    Functions include parameter types, return types, and any decorators.
    """
    lines = ["Module-Level Functions Documentation", "=" * 40, ""]
    for pkg, module_entries in sorted(modules.items()):
        lines.append(f"Package: {pkg}")
        for entry in sorted(module_entries, key=lambda e: e["module"]):
            lines.append(f"  Module: {entry['module']}")
            for func_name, info in sorted(entry["functions"].items()):
                param_str = ", ".join(info["params"])
                signature = f"{func_name}({param_str})"
                if info["return"]:
                    signature += f" -> {info['return']}"
                if info.get("decorators"):
                    decorator_str = ", ".join(info["decorators"])
                    signature += f" [Decorators: {decorator_str}]"
                lines.append(f"    - {signature}")
            lines.append("")
        lines.append("")
    return "\n".join(lines)

# --------------------------------------------------
# Parsing and Documenting Site Content (HTML, JS, CSS)
# --------------------------------------------------

def parse_site_content(root_dir):
    """
    Walks the directory tree and finds all .html, .js, and .css files.
    Returns a list of dictionaries, each containing the file's relative path and its content.
    """
    site_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(('.html', '.js', '.css')):
                filepath = os.path.join(dirpath, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    content = f"Error reading file: {e}"
                relative_path = os.path.relpath(filepath, root_dir)
                site_files.append({
                    "path": relative_path,
                    "content": content
                })
    return site_files

def generate_site_content_doc(site_files):
    """
    Generates a plain-text documentation of the site content.
    For each file, its relative path is printed along with its full content.
    """
    lines = ["Site Content Documentation", "=" * 40, ""]
    for file_info in sorted(site_files, key=lambda x: x["path"]):
        header = f"File: {file_info['path']}"
        lines.append(header)
        lines.append("-" * len(header))
        lines.append(file_info["content"])
        lines.append("\n" + "=" * 40 + "\n")
    return "\n".join(lines)

# --------------------------------------------------
# Main Functionality (Generating Three Docs)
# --------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate UML diagram text for classes, documentation for module-level functions (with decorators), and site content documentation (HTML, JS, CSS) from a Python code base."
    )
    parser.add_argument("--root", required=True,
                        help="Root directory of the Python project to generate documentation from.")
    parser.add_argument("-o", "--output", default=".",
                        help="Output folder for the generated files (uml.txt, module_functions.txt, and site-content.txt). Defaults to current directory.")
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        print(f"Error: The specified root directory '{args.root}' does not exist or is not a directory.")
        sys.exit(1)

    output_folder = os.path.abspath(args.output)
    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
        except Exception as e:
            print(f"Error creating output folder '{output_folder}': {e}")
            sys.exit(1)

    print(f"Parsing Python project at '{args.root}'...")

    # Generate UML for classes.
    packages = parse_directory(args.root)
    uml_source = generate_plantuml(packages)
    uml_txt_path = os.path.join(output_folder, "uml.txt")
    try:
        with open(uml_txt_path, "w", encoding="utf-8") as f:
            f.write(uml_source)
        print(f"PlantUML source (classes) saved to: {uml_txt_path}")
    except Exception as e:
        print(f"Error writing UML source to file: {e}")
        sys.exit(1)

    # Generate documentation for module-level functions.
    module_funcs = parse_directory_module_functions(args.root)
    module_funcs_doc = generate_module_functions_doc(module_funcs)
    module_funcs_txt_path = os.path.join(output_folder, "module_functions.txt")
    try:
        with open(module_funcs_txt_path, "w", encoding="utf-8") as f:
            f.write(module_funcs_doc)
        print(f"Module-level functions documentation saved to: {module_funcs_txt_path}")
    except Exception as e:
        print(f"Error writing module functions documentation to file: {e}")
        sys.exit(1)

    # Generate site content documentation.
    site_files = parse_site_content(args.root)
    site_content_doc = generate_site_content_doc(site_files)
    site_content_txt_path = os.path.join(output_folder, "site-content.txt")
    try:
        with open(site_content_txt_path, "w", encoding="utf-8") as f:
            f.write(site_content_doc)
        print(f"Site content documentation saved to: {site_content_txt_path}")
    except Exception as e:
        print(f"Error writing site content documentation to file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
