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
    NO PIP TOOLS where provided...
{% endif %}