# Asymptomatic
A portmanteau of "automatic" and "asymptote".  We're all aware of the [Geogebra diagram to Asymptote conversion](https://www.geogebra.org/classic?lang=en) written by Azjps about a decade or so ago.  While this does its job well, I think anyone who's used this tool knows that quite a bit of effort has to go into making the diagram *usable*.

Asymptomatic is an attempt at automating this process!

# Usage
1. Make a diagram at [Classic Geogebra](https://www.geogebra.org/classic?lang=en) and export it as an Asymptote .txt file.  This should save as "geogebra-export.txt" (if it saves as "geogebra-export-n.txt" or "geogebra-export(n).txt, rename it "geogebra-export.txt", or dig through the main.py file below to change the file it opens manually (not advised, but it's at the bottom of the file in "input_file", if you really want to do it)).
2. [Download Python 3](https://www.python.org/downloads/), if for whatever reason you still don't have it.
3. Download main.py here.  Store it in some folder where you want to do your geogebra diagram converting.
4. Move "geogebra-export.txt" from before into this folder.
5. Run "python3 main.py" and create a file called "geogebra-export-modified.txt" in the terminal.
6. Enjoy the new file!

# Credits and License
Licensed under the MIT License.  Do what you want with it, I don't care.

Made by Charles Zhang, because I was bored, and because I hate manually editing the exported file.
