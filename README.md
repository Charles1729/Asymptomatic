# Asymptomatic
A portmanteau of "automatic" and "asymptote".  We're all aware of the [Geogebra diagram to Asymptote conversion](https://www.geogebra.org/classic?lang=en) written by [Azjps](https://artofproblemsolving.com/wiki/index.php/User:Azjps/geogebra) about [a decade or so ago](https://i.imgur.com/J3WfHEf.png).  While this does its job well, I think anyone who's used this tool to make [Olympiad geometry](https://web.evanchen.cc/geombook.html) or [math contest geometry](https://maa.org/student-programs/amc/) diagrams knows that quite a bit of effort has to go into making the diagram *usable*.

Asymptomatic is an attempt at automating this process!  This is currently a work in progress.  Suggest features!  See below on how to contact me.

# Usage
1. Make a diagram at [Classic Geogebra](https://www.geogebra.org/classic?lang=en) and export it as an Asymptote .txt file.  This should save as "geogebra-export.txt" (if it saves as "geogebra-export-n.txt" or "geogebra-export(n).txt, rename it "geogebra-export.txt", or dig through the main.py file below to change the file it opens manually (not advised, but it's at the bottom of the file in "input_file", if you really want to do it)).
2. [Download Python 3](https://www.python.org/downloads/), if for whatever reason you still don't have it.
3. Download main.py here.  Store it in some folder where you want to do your geogebra diagram converting.
4. Move "geogebra-export.txt" from before into this folder.
5. Move into the folder (directory) with the "cd" command [in the terminal](https://tutorials.codebar.io/command-line/introduction/tutorial.html).
6. Run "python3 main.py" in the terminal and watch as a a file called "geogebra-export-modified.txt" is created.
7. Open the new file.  The first line should say something about "size(0cm);".  Adjust this according to how big you want the diagram to be.
8. Enjoy!

# Product
See demo.txt above for some idea of what the product of this program does specifically, and how it formats things.

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
