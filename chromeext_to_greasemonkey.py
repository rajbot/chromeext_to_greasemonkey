#!/usr/bin/env python

"""Converts a simple chrome extension to a greasemonkey script

This script takes one parameter: the path to an unpacked chrome extension directory.
The directory should contain a manifest.json file.

If manifest.json does not specify an author, the default_author variable will be used.
"""

import cssmin
import json
import os
import sys

default_author = 'rajbot'
chrome_dir = sys.argv[1]
manifest_path = os.path.join(chrome_dir, 'manifest.json')
manifest = json.load(open(manifest_path))

author      = manifest.get('author', default_author)
name        = manifest.get('name')
version     = manifest.get('version')
description = manifest.get('description')

content_scripts = manifest.get('content_scripts')
if len(content_scripts) != 1:
    sys.exit('Error: this script requires exactly one content_scripts array entry')

if sorted(content_scripts[0].keys()) != [u'css', u'matches']:
    sys.exit('Error: this script can only handle css files in the content_scripts array')

includes  = content_scripts[0]['matches']
css_files = content_scripts[0]['css']

css = ''
for f in css_files:
    path = os.path.join(chrome_dir, f)
    css += cssmin.cssmin(open(path).read())
if "'" in css:
    sys.exit('Error: css files can not contain a single-quote, since it will break the generated javascript')
if "\n" in css:
    sys.exit('Error: minified css contains newline.')


print """// ==UserScript==
// @name           {n}
// @version        {v}
// @author         {a}
// @description    {d}
// @grant          GM_addStyle
""".format(n=name, v=version, a=author, d=description),

for i in includes:
    print "// @include        {i}".format(i=i)

print "// ==/UserScript==\n"
print "// This script was generated programatically by chromeext_to_greasemonkey.py\n"

print "(function() {"
print "    GM_addStyle('{css}');\n".format(css=css)
print "})();"
