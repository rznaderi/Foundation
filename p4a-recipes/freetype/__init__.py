from pythonforandroid.recipe import CythonRecipe


class FreetypeRecipe(CythonRecipe):
    version = "2.14.1"
    url = "https://nongnu.uib.no/freetype/freetype-{version}.tar.gz"
    name = "freetype"


recipe = FreetypeRecipe()
