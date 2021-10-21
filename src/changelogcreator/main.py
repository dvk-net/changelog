import argparse
import subprocess
import re
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from bs4 import BeautifulSoup
# args.image = '8fe56664df0a'
template_name = 'toolset.md'
output_filename = 'changelog.md'

regex = r"^FROM .*"

parser = argparse.ArgumentParser(
    description='Creates changelog file based on toolset.xml. Extracts version from docker container, using toolset.md template')

parser.add_argument('--image', type=str, required=True,
                    help='an image ID or an image name')

parser.add_argument('--outpath', type=str, required=True,
                    help='Path for generated changelog')
parser.add_argument('--dockerfile', type=str, required=True,
                    help='path to dockerfile')
parser.add_argument('--mode', type=str, default='append', choices=['append', 'create'], required=False,
                    help='either create new changelog file or append to existing one')
args = parser.parse_args()

DOCKER_FILE = Path(args.dockerfile).resolve()
OUTPUT_FILE = Path(args.outpath).resolve()

context = {} # the dict to be sent for being rendered in the template
context['BASE_IMAGE'] = "NOT DEFINED"

env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape()
)

template = env.get_template(template_name)


def make_bold(match_obj):
    if match_obj.group(1) is not None:
        return " **" + match_obj.group(1) + "** "


def tool_info_extractor(soup, tool, is_version_in_json=False):
    """Parse tool's name and command to get version info.
    Run extracted command in docker container 
    Returns List

    Args:
        soup (BeautifulSoup): BeautifulSoup object with toolset xml
        tool (str): Toolname in toolset xml
        is_version_in_json (bool): If version needs to parsed as json

    Returns:
        list: Returns List(dict) with 'name' and 'version' 
    """
    out = []
    for command in soup.find_all(tool):
        cmd = command.find('command-to-check-version').text.split(" ")
        bash_cmd = ['docker', 'run', args.image, *cmd]
        process = subprocess.Popen(bash_cmd, stdout=subprocess.PIPE)
        output, error = process.communicate()
        if not error:
            if not is_version_in_json:
                version = re.sub(r"([\w\-]+:) ", make_bold, output.decode())
            else:
                version = json.loads(output.decode())
            out.append({
                'name': command.find('name').text,
                'version': version})
        else:
            out.append({
                'name': command.find('name').text,
                'version': "Not present or error"})
    return out


with open(DOCKER_FILE, "r") as fp:
    # base image info parser
    text = fp.read()
    from_image = re.findall('FROM (.*)', text)
    if from_image:
        context['BASE_IMAGE'] = from_image[0]

with open('toolset.xml', 'r') as fp:
    soup = BeautifulSoup(fp, "xml")


context['APT_TOOLS'] = tool_info_extractor(soup, 'apt-tool')
context['PIP_TOOLS'] = tool_info_extractor(soup, 'python-pip-tool')
context['AZURE_CLI_TOOLS'] = tool_info_extractor(soup, 'azure-cli-tool')
if from_image:
    context['BASE_IMAGE'] = from_image[0]

output = template.render(context)

if args.mode == 'create':
    mode = 'w'
else:
    mode = 'a'
with open(OUTPUT_FILE, mode) as fp:
    fp.write(output)
