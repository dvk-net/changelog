# changelog python utility

The utility for extracting info about installed (used) tools inside docker container

## Usage

1. Clone repo or 

    ```bash
    pip install -U git+<repo URL>
    ```

1. Run it
    ```bash
    python3 main.py ..params 
    ```
    or
    ```
    docker-changelog-creator ..params
    ```
    where params are:
    ```bash
    Creates changelog file based on toolset.xml. Extracts version from docker container, using toolset.md template

    optional arguments:
    -h, --help            show this help message and exit
    --image IMAGE         an image ID or an image name
    --outpath OUTPATH     Path for generated changelog
    --dockerfile DOCKERFILE
                            path to dockerfile
    --toolstotestfile TOOLSTOTESTFILE
                            path to the xml file with tools for extracting info
    --outputtemplatefile OUTPUTTEMPLATEFILE
                            path to Junja2 template file for rendering and createtin well-formated changelog
    --mode {append,create}
                        either create new changelog file or append to existing one
    ```
1. Tools to testfile example
    ```xml
    <tools>
        <apt-tools>
            <apt-tool>
                <name>Python 2</name>
                <command-to-check-version>apt-cache show python2</command-to-check-version>
            </apt-tool>
            <apt-tool>
                <name>Python 3.8</name>
                <command-to-check-version>apt-cache show python3.8</command-to-check-version>
            </apt-tool>
            <apt-tool>
                <name>Python 3.11</name>
                <command-to-check-version>apt-cache show python3.11</command-to-check-version>
            </apt-tool>
        </apt-tools>
        <python-pip-tools>
            <python-pip-tool>
                <name>python conan package</name>
                <command-to-check-version>pip show conan</command-to-check-version>
            </python-pip-tool>
        </python-pip-tools>
        <azure-cli-tools>
            <azure-cli-tool>
                <name>Azure CLI</name>
                <command-to-check-version>az version</command-to-check-version>
            </azure-cli-tool>
        </azure-cli-tools>
    </tools>
    ```
1. Jinja2 template example(https://jinja.palletsprojects.com/en/3.0.x/templates/):
    ```jinja
    # TOOLS

    ## Base image: {{BASE_IMAGE}}



    {% if APT_TOOLS %}
    ## APT TOOLS

    {% for pkg in APT_TOOLS %}
    --------------------------
    ## {{ pkg.name }}
    <pre>{{ pkg.version|replace("\n", "<br>")|default("Not found", true) }}</pre>
    --------------------------
    {% endfor %}
    {% else %}
        NO APT TOOLS where provided...
    {% endif %}


    {% if PIP_TOOLS %}
    ## APT TOOLS

    {% for pkg in PIP_TOOLS %}
    --------------------------
    ## {{ pkg.name }}
    <pre>{{ pkg.version|replace("\n", "<br>")|default("Not found", true) }}</pre>
    --------------------------
    {% endfor %}
    {% else %}
        NO PIP TOOLS where provided...
    {% endif %}


    {% if AZURE_CLI_TOOLS %}
    ## AZURE CLI TOOLS

    {% for pkg in AZURE_CLI_TOOLS %}
    --------------------------
    ## {{ pkg.name }}

    **azure-cli**: {{pkg['version']['azure-cli']}}<br> 
    **azure-cli-core**: {{pkg['version']['azure-cli-core']}} <br> 
    **azure-cli-telemetry**: {{pkg['version']['azure-cli-telemetry']}} <br> 

    --------------------------
    {% endfor %}
    {% else %}
        NO AZURE CLI TOOLS where provided...
    {% endif %}
    ```