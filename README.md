# Facebook Message Export Parser

Facebook has a feature that allows users to download a copy of their data as a zip archive containing htm files with their data. The aim of this parser is to take this archive and to extract a user's Facebook Messages from it; to transfer them into a more useful format, as well as performing some analysis to produce interesting data.

This code is adapted from [CopOnTheRun/FB-Message-Parser](https://github.com/CopOnTheRun/FB-Message-Parser).

#### Running the Code
The Facebook Export can be downloaded from  the [Facebook Settings](https://www.facebook.com/settings) menu. 

__*Before any code can be run:*__ [Lines 26 and 27](https://github.com/jsharkey13/facebook_message_parser/blob/master/fb_parser.py#L27-L28) in `fb_parser.py` will need to be updated to the name and username of the account being parsed. If this is done, the code will attempt to open the zip file `facebook-[myusername].zip` by default if no argument is given to `facebook.py`.
If the locale of the export is not the UK, then some other lines may need editing. If the timestamp of the messages doesn't match the date format e.g. `Friday, 1 January 2016 at 01:01 UTC` then [line 26](https://github.com/jsharkey13/facebook_message_parser/blob/master/fb_parser.py#L26) in `fb_parser.py` will also need to be changed: see the [Python docs](https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior) for help here. The code on [lines 137-147](https://github.com/jsharkey13/facebook_message_parser/blob/master/fb_parser.py#L137-L147) of the same file may also need editing to reflect the locale's summer time convention.

Run "`python facebook.py [optional_filename]`" with the `facebook-[myusername].zip` or `messages.htm` files in the same directory to export to CSV, display top 10 most messaged friends and output a graph showing messages with the most messaged friend. This sample code can easily be adapted.

__Producing Graphs__

The `fb_analysis.py` file contains code to produce a stacked histogram showing the number of messages sent and recieved with a contact each month:

![Sample Graph](/samples/sample_date_graph.png?raw=true)


#### Dependencies
The code is written in Python 2.7.

The parser uses [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/) to do the bulk of the capture from the htm file.

The analysis code uses [matplotlib](http://matplotlib.org/) to produce graphs of message counts. An example graph can be found in the `samples` directory.

[Anaconda Python](https://store.continuum.io/cshop/anaconda/) for scientific computing is a simple and easy way to install all the dependencies for the code, alongside many other useful libraries. It can be downloaded [here](http://continuum.io/downloads).
