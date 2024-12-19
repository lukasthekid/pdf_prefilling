from io import BytesIO
from typing import Dict

import yaml
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject
from jinja2 import Template, UndefinedError

from application.models.Person import Person


def load_mapping_config(config_path: str) -> Dict[str, str]:
    """
    Loads the mapping configuration from a YAML or JSON file.

    Args:
        config_path (str): Path to the mapping configuration file.

    Returns:
        Dict[str, str]: A dictionary mapping PDF fields to Jinja2 templates.
    """
    if config_path.endswith('.yaml') or config_path.endswith('.yml'):
        with open(config_path, 'r', encoding='utf-8') as file:
            mapping = yaml.safe_load(file)
    else:
        raise ValueError("Unsupported configuration file format. Use .yaml or .json")

    if not isinstance(mapping, dict):
        raise ValueError("Mapping configuration must be a dictionary")

    return mapping


def render_pdf_fields(customer: Person, mapping_config: Dict[str, str]) -> Dict[str, str]:
    """
    Renders the PDF field values based on the mapping configuration.

    Args:
        customer (CustomerDTO): The customer data transfer object.
        mapping_config (Dict[str, str]): Mapping configuration.

    Returns:
        Dict[str, str]: A dictionary mapping PDF fields to their rendered values.
    """
    rendered_fields = {}
    # Convert the customer DTO to a dict, including nested enums and date formatting
    customer_data = customer.dict()

    # Add additional attributes or methods if needed
    # For example, ensure that birthdate is a datetime.date object

    for pdf_field, template_str in mapping_config.items():
        try:
            template = Template(template_str)
            rendered_value = template.render(**customer_data)
            rendered_fields[pdf_field] = rendered_value
        except UndefinedError as e:
            print(f"Undefined variable in template for field '{pdf_field}': {e}")
            rendered_fields[pdf_field] = ""
        except Exception as e:
            print(f"Error rendering field '{pdf_field}': {e}")
            rendered_fields[pdf_field] = ""

    rendered_fields[customer.gender] = "/Yes"
    return rendered_fields


def fill_pdf(input_pdf: str, data: Dict[str, str]):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Ensure appearances are updated
    if "/AcroForm" in writer._root_object:
        writer._root_object["/AcroForm"].update({NameObject("/NeedAppearances"): NameObject("/True")})

    for page in reader.pages:
        writer.add_page(page)

    for page_number in range(len(writer.pages)):
        writer.update_page_form_field_values(writer.pages[page_number], data)

    output_buffer = BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)
    return output_buffer
