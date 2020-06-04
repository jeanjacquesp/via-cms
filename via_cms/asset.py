#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

from flask_assets import Bundle
from flask_assets import Environment


theme = 'cerulean'

# js = Bundle("_vendor/jQuery/3.4.1/jquery-3.4.1.min.js", "_vendor/bootstrap/4.3.1/dist/js/bootstrap.bundle.js",
#             "_vendor/jquery-ui/1.12.1/jquery-ui.min.js",
#             "_vendor/fancytree/2.31.0/dist/jquery.fancytree-all.min.js", "_fordev/js/jqscript.js",
#             "_fordev/js/script.js", filters='jsmin', output="bundle/js/project-via.js")
#
# css = Bundle("_vendor/font-awesome/5.9.0/css/fontawesome.min.css",
#              "_vendor/bootswatch/4.3.1/dist/{!s}/bootstrap.min.css".format(theme),
#              "_vendor/jquery-ui/1.12.1/jquery-ui.min.css",
#              "_vendor/fancytree/2.31.0/dist/skin-win8/ui.fancytree.min.css", "_fordev/css/style.css",
#              filters="cssmin", output="bundle/css/project-via.css")
#
# css_rtl = Bundle("_vendor/font-awesome/5.9.0/css/fontawesome.min.css",
#                  "_vendor/bootswatch/4.3.1/dist/{!s}/bootstrap.min.css".format(theme),
#                  "_vendor/jquery-ui/1.12.1/jquery-ui.min.css",
#                  "_vendor/fancytree/2.31.0/dist/skin-win8/ui.fancytree.min.css",
#                  "_fordev/css/style-rtl.css", filters="cssmin", output="bundle/css/project-via-rtl.css")

js = Bundle("_vendor/jQuery/3.5.1/jquery-3.5.1.min.js", "_vendor/bootstrap/4.4.1/dist/js/bootstrap.bundle.js",
            "_vendor/jquery-ui/1.12.1/jquery-ui.min.js",
            "_vendor/fancytree/2.35.0/dist/jquery.fancytree-all.min.js",
            "_fordev/js/jqscript.js",
            "_fordev/js/script.js",
            filters='jsmin',
            output="bundle/js/project-via.js")

css = Bundle("_vendor/font-awesome/5.13.0/css/fontawesome.min.css",
             "_vendor/bootswatch/4.4.1/dist/{!s}/bootstrap.min.css".format(theme),
             "_vendor/jquery-ui/1.12.1/jquery-ui.min.css",
             "_vendor/fancytree/2.35.0/dist/skin-win8/ui.fancytree.min.css",
             "_fordev/css/style.css",
             filters="cssmin",
             output="bundle/css/project-via.css")

css_rtl = Bundle("_vendor/font-awesome/5.13.0/css/fontawesome.min.css",
                 "_vendor/bootswatch/4.4.1/dist/{!s}/bootstrap.min.css".format(theme),
                 "_vendor/jquery-ui/1.12.1/jquery-ui.min.css",
                 "_vendor/fancytree/2.35.0/dist/skin-win8/ui.fancytree.min.css",
                 "_fordev/css/style-rtl.css",
                 filters="cssmin",
                 output="bundle/css/project-via-rtl.css")

asset = Environment()

asset.register("js_all", js)
asset.register("css_all", css)
asset.register("css_all_rtl", css_rtl)
