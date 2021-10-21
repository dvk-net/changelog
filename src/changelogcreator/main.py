import argparse
import subprocess
import re
import json
from pathlib import Path
from sys import stderr
from jinja2 import Environment, FileSystemLoader, select_autoescape
from bs4 import BeautifulSoup

regex = r"^FROM .*"


def make_bold(match_obj):
    if match_obj.group(1) is not None:
        return " **" + match_obj.group(1) + "** "


def tool_info_extractor(soup, tool, script_args, is_version_in_json=False):
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
        bash_cmd = ['docker', 'run', script_args.image, *cmd]
        process = subprocess.Popen(bash_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
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


def main():
    parser = argparse.ArgumentParser(
        description='''Creates changelog file based on jinja2 template. Extracts versions from docker image, using xml description. Parses BASE IMAGE from Dockerfile''')

    parser.add_argument('--image', type=str, required=True,
                        help='an image ID or an image name')

    parser.add_argument('--outpath', type=str, required=True,
                        help='Path for generated changelog')
    parser.add_argument('--dockerfile', type=str, required=True,
                        help='path to dockerfile')
    parser.add_argument('--toolstotestfile', type=str, required=True,
                        help='path to the xml file with tools for extracting info')
    parser.add_argument('--outputtemplatefile', type=str, required=True,
                        help='path to Junja2 template file for rendering and createtin well-formated changelog')
    parser.add_argument('--mode', type=str, default='append', choices=['append', 'create'], required=False,
                        help='either create new changelog file or append to existing one')
    args = parser.parse_args()

    TOOLSET_FILE = Path(args.toolstotestfile).resolve()
    OUTPUT_FILE = Path(args.outpath).resolve()
    OUTPUTTEMPLATE_FILE = Path(args.outputtemplatefile).resolve().name
    OUTPUTTEMPLATE_DIR = Path(args.outputtemplatefile).resolve().parent
    DOCKER_FILE = Path(args.dockerfile).resolve()
    context = {}  # the dict to be sent for being rendered in the template
    context['BASE_IMAGE'] = "NOT DEFINED"

    env = Environment(
        loader=FileSystemLoader(OUTPUTTEMPLATE_DIR),
        autoescape=select_autoescape()
    )

    template = env.get_template(OUTPUTTEMPLATE_FILE)

    with open(DOCKER_FILE, "r") as fp:
        # base image info parser
        text = fp.read()
        from_image = re.findall('FROM (.*)', text)
        if from_image:
            context['BASE_IMAGE'] = from_image[0]

    with open(TOOLSET_FILE, 'r') as fp:
        soup = BeautifulSoup(fp, "xml")

    context['APT_TOOLS'] = tool_info_extractor(soup, 'apt-tool', args)
    context['PIP_TOOLS'] = tool_info_extractor(soup, 'python-pip-tool', args)
    context['AZURE_CLI_TOOLS'] = tool_info_extractor(
        soup, 'azure-cli-tool', args, is_version_in_json=True)

    if from_image:
        context['BASE_IMAGE'] = from_image[0]

    output = template.render(context)

    if args.mode == 'create':
        mode = 'w'
    else:
        mode = 'a'
    with open(OUTPUT_FILE, mode) as fp:
        fp.write(output)


if __name__ == "__main__":
    main()
