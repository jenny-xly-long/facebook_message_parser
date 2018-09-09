# Facebook Message Export Parser

---
## Update September 2018

__Deprecation Notice__

Facebook now support exports in JSON format, which somewhat reduces the need for this code. The format of these exports has changed a great deal, and is still changing. This code will not work with exports newer than April 2018.

Some (unmaintained) code that may work with newer JSON exports can be found [in this Gist](https://gist.github.com/jsharkey13/d60b7b421e08c98d426d03c39f8b4a12), but be aware that code is Python 3 and the format of Facebook's export may have changed since it was written.

---

Facebook has a feature that allows users to download a copy of their data as a zip archive containing htm files with their data. The aim of this parser is to take this archive and to extract a user's Facebook Messages from it; to transfer them into a more useful format, as well as performing some analysis to produce interesting data.

This code is adapted from [CopOnTheRun/FB-Message-Parser](https://github.com/CopOnTheRun/FB-Message-Parser).

#### Running the Code
The Facebook Export can be downloaded from  the [Facebook Settings](https://www.facebook.com/settings) menu. 

__*Before any code can be run:*__ [Lines 26 and 27](https://github.com/jsharkey13/facebook_message_parser/blob/master/fb_parser.py#L27-L28) in `fb_parser.py` will need to be updated to the name and username of the account being parsed. If this is done, the code will attempt to open the zip file `facebook-[myusername].zip` by default if no argument is given to `facebook.py`.

Run "`python facebook.py [optional_filename]`" with the `facebook-[myusername].zip` or `messages.htm` files in the same directory to export to CSV, display top 10 most messaged friends and output a graph showing messages with the most messaged friend. This sample code can easily be adapted.

The `fb_chat.Chat` object returned by the parser (the object called `Facebook.Chat` in `facebook.py`) could be pickled and loaded in another program to form a base API to interact with the messages there. (Note that this, like the export, contains private messages in plain text format, and that the `fb_chat` code may need to be imported too).

__Producing Graphs__

The `fb_analysis.py` file contains code to produce a stacked histogram showing the number of messages sent and recieved with a contact each month:

![Sample Graph](/samples/sample_date_graph.png?raw=true)

__A browser-based interface__

If you want to view the export in a browser (and don't want to use the perfectly servicable way of viewing Facebook Messages in a browser that is `www.facebook.com`) then [Flask Facebook Messages](https://github.com/jsharkey13/flask_facebook_messages) may be of use. Add `Facebook.dump_to_pickle()` on a new line after [Line 52](https://github.com/jsharkey13/facebook_message_parser/blob/master/facebook.py#L52) of `facebook.py` to produce a pickle export, then use the code in that repository to view it!

#### Dependencies
The code is written in Python 2.7.

The parser uses [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/) to do the bulk of the capture from the htm file.

The analysis code uses [matplotlib](https://matplotlib.org/) to produce graphs of message counts. An example graph can be found in the `samples` directory.

[Anaconda Python](https://store.continuum.io/cshop/anaconda/) for scientific computing is a simple and easy way to install all the dependencies for the code, alongside many other useful libraries. It can be downloaded [here](https://www.continuum.io/downloads).
