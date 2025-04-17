# Asymptomatic
A portmanteau of "automatic" and "asymptote".  We're all aware of the [Geogebra diagram to Asymptote conversion](https://www.geogebra.org/classic?lang=en) written by [Azjps](https://artofproblemsolving.com/wiki/index.php/User:Azjps/geogebra) about [a decade or so ago](https://i.imgur.com/J3WfHEf.png).  While this does its job well, I think anyone who's used this tool to make [Olympiad geometry](https://web.evanchen.cc/geombook.html) or [math contest geometry](https://maa.org/student-programs/amc/) diagrams knows that quite a bit of effort has to go into making the diagram *usable*.

Asymptomatic is an attempt at automating this process!  This is currently a work in progress.  Suggest features!  See below on how to contact me.

# Usage
## Slightly Hacky, For People Who "just want it to work"
1. Make a diagram at [Classic Geogebra](https://www.geogebra.org/classic?lang=en) (or the [app](https://www.geogebra.org/download?lang=en)) and export it as an Asymptote .txt file.  This should save as "geogebra-export.txt" (if it saves as "geogebra-export-n.txt" or "geogebra-export(n).txt, just change the running line below).  This is your input file.
2. [Download Python 3](https://www.python.org/downloads/), if for whatever reason you still don't have it.
3. Download main.py here.  Store it in the same folder where your input file is.
4. Move into that folder (directory) with the "cd" command [in the terminal](https://tutorials.codebar.io/command-line/introduction/tutorial.html).
5. Run ```python3 main.py geogebra-export.txt output.txt 3```. The "geogebra-export.txt" is your input file, "output.txt" is the filename of what will be produced by the program, and the "3" is however many digits after the decimal you want to truncate numbers to.
6. Open the new file.  The first line should say something about "size(0cm);".  Adjust this according to how big you want the diagram to be.
7. Use in your LaTeX, wherever you compile it.
8. Enjoy!
## More Advanced, For People Who Know What Filepaths Are
1. Follow steps 1-3 above.
2. Store the main.py file in some directory where you want to keep it.  Copy down the filepath
3. Run ```python3 /the/file/path/to/this/main.py /probably/in/Downloads/geogebra-export.txt /wherever/you/want/output.txt 3```
5. Save this command somehow ([zshrc on Macs](https://superuser.com/questions/886132/where-is-the-zshrc-file-on-mac) are really good for this.  Save it as an alias if you want.)
6. Follow 6-8 as before.

# Product
See the Demo folder for an idea of what this does.

# Oh no!  There's something weird/wrong/error with my exported file!
~~Deal with it~~ Shoot me a quick email at charleszhang1729 (at) gmail (dot) com or DM me on Discord (at) contabulator (preferred) with the following:
- What file you fed into the program and what it spat out;
- Which lines you think are problematic in the output file;
- What you expected those lines to look like (if this is for an Asymptote error, you can ignore this);
and I *might* get back to you or fix this.

Otherwise, if you are one of the magical wizards who [knows how to use pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request), then do that.

# Credits and License
Licensed under the MIT License.  Do what you want with it, I don't care.

Made by Charles Zhang, because I was bored, and because I hate manually editing the exported file.
