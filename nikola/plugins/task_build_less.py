# -*- coding: utf-8 -*-

# Copyright © 2012-2013 Roberto Alsina and others.

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import unicode_literals

import codecs
import glob
import os
import subprocess

from nikola.plugin_categories import Task
from nikola import utils


class BuildLess(Task):
    """Bundle assets using WebAssets."""

    name = "build_less"

    def gen_tasks(self):
        """Generate CSS out of LESS sources."""

        kw = {
            'cache_folder': self.site.config['CACHE_FOLDER'],
            'themes': self.site.THEMES,
        }

        # Find where in the theme chain we define the LESS targets
        # There can be many *.less in the folder, but we only will build
        # the ones listed in less/targets
        targets_path = utils.get_asset_path(os.path.join("less","targets"), self.site.THEMES)
        with codecs.open(targets_path, "rb", "utf-8") as inf:
            targets = [x.strip() for x in inf.readlines()]

        # Create a temporary folder and merge all the LESS sources from the theme chain
        
        # Build targets and write CSS files
        base_path = utils.get_theme_path(self.site.THEMES[0])
        dst_dir = os.path.join(base_path, "assets", "css")
        # Make everything depend on all sources, rough but enough
        deps = glob.glob(os.path.join(base_path, "*.less"))
        
        def compile_target(target, dst):        
            if not os.path.isdir(dst_dir):
                os.makedirs(dst_dir)
            src = os.path.join(base_path, "less", target)
            compiled = subprocess.check_output(["lessc", src])
            with open(dst, "wb+") as outf:
                outf.write(compiled)

        for target in targets:
            dst = os.path.join(dst_dir, target.replace(".less", ".css"))
            yield {
                'basename': self.name,
                'name': dst,
                'targets': [dst],
                'file_dep': deps,
                'actions': ((compile_target, [target, dst]), ),
                'uptodate': [utils.config_changed(kw)],
                'clean': True
            }

        if not targets:
            yield {'basename': self.name, 'actions': []}
        
