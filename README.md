# Asymptomatic
A portmanteau of "automatic" and "asymptote".  We're all aware of the [Geogebra diagram to Asymptote conversion](https://www.geogebra.org/classic?lang=en) written by Azjps about a decade or so ago.  While this does its job well, I think anyone who's used this tool knows that quite a bit of effort has to go into making the diagram *usable*.

Asymptomatic is an attempt at automating this process!  This is currently a work in progress.  Suggest features!

# Usage
1. Make a diagram at [Classic Geogebra](https://www.geogebra.org/classic?lang=en) and export it as an Asymptote .txt file.  This should save as "geogebra-export.txt" (if it saves as "geogebra-export-n.txt" or "geogebra-export(n).txt, rename it "geogebra-export.txt", or dig through the main.py file below to change the file it opens manually (not advised, but it's at the bottom of the file in "input_file", if you really want to do it)).
2. [Download Python 3](https://www.python.org/downloads/), if for whatever reason you still don't have it.
3. Download main.py here.  Store it in some folder where you want to do your geogebra diagram converting.
4. Move "geogebra-export.txt" from before into this folder.
5. Move into the folder (directory) with the "cd" command in the terminal.
6. Run "python3 main.py" in the terminal and watch as a a file called "geogebra-export-modified.txt" is created.
7. Open the new file.  The first line should say something about "size(0cm);".  Adjust this according to how big you want the diagram to be.
8. Enjoy!

# Oh no!  The exported file has an error/weird behavior/something wrong with it!
~~Deal with it~~ Shoot me a quick email at charleszhang1729 (at) gmail (dot) com or DM me on Discord (at) contabulator (preferred) with the following:
- What file you fed into the program and what it spat out;
- Which lines you think are problematic in the output file;
- What you expected those lines to look like;

and I *might* get back to you or change this.

Otherwise, if you are one of the magical wizards who [knows how to use pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request), then do that.

# Credits and License
Licensed under the MIT License.  Do what you want with it, I don't care.

Made by Charles Zhang, because I was bored, and because I hate manually editing the exported file.
