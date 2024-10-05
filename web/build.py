from pathlib import Path
from os import path
# parent is the directory containing the file
webdir = Path(__file__).parent

from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader(webdir.joinpath("templates")),
    autoescape=select_autoescape()
)

groupsdir = webdir.parent.resolve()
grouppaths = sorted(groupsdir.glob("*.yaml"))

from json import loads
schema = loads(open(groupsdir.joinpath("defengroup.schema.json")).read())

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# load all group data into groups, with stem (filename w/o extension) as key
groups = {p.stem: load(open(p.name), Loader) for p in grouppaths}

# write the list of groups (left iframe in index.html)
listtpl = env.get_template("list.html")
htmlfile = open(webdir.joinpath("list.html"), "w")
htmlfile.write(listtpl.render(groups=groups))

# json schema is used to validate the yaml files
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError, SchemaError
validator = Draft202012Validator(schema)
grouptpl = env.get_template("group.html")
# render each group's page
for gid, group in groups.items():
    # https://python-jsonschema.readthedocs.io/en/stable/validate/
    messages = [e.message for e in validator.iter_errors(group)]
    success = len(messages) < 1
    
    htmlfile = open(webdir.joinpath(gid + ".html"), "w")
    htmlfile.write(grouptpl.render(group=group, vsuccess=success, vmessages=messages))
