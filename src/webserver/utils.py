import os 
import sys
sys.path.append("src")
from scraping.adapters import get_adapter_by_name

examples_path = "examples/html"

def prepare_file(file, type=None, save=None, sectionize=True, wrap_text=True):
    if type is None:
        type = os.path.split(file)[-2]
        file = os.path.join(examples_path, file)
    else:
        file = os.path.join(examples_path, type, file)
    adap = get_adapter_by_name(type, file, sectionize=sectionize, wrap_text=wrap_text)
    if save:
        adap.save(save)
    return adap._soup.prettify()

def list_examples():
    policies = {}
    folders = sorted(os.listdir(examples_path))
    for folder in folders:
        policies[folder] = sorted(os.listdir(os.path.join(examples_path, folder)))
    return policies

def get_example_file(type, file):
    return os.path.join(examples_path, type, file)