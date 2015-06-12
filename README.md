# Facebook Message Export Parser

Facebook has a feature that allows users to download a copy of their data as a zip archive containing htm files with their data. The aim of this parser is to take this archive and to extract a user's Facebook Messages from it; to transfer them into a more useful format, as well as performing some analysis to produce interesting data.


#### Running the Code
The Facebook Export can be downloaded from  the [Facebook Settings](https://www.facebook.com/settings) menu. 

Run "`python facebook.py [zip_archive_file_name or messages_htm_file_name]`" with the `facebook-[myusername].zip` or `messages.htm` files in the same directory to export to CSV, display top 10 most messaged friends and output a graph showing messages with the most messaged contact.

__*Lines 39-40 in `facebook.py` will need to be updated to the name and username of the account being parsed*__. If this is done, the code will attempt to open the zip file `facebook-[myusername].zip` by default if no argument is given to `facebook.py`.

__Producing Graphs__

The `fb_analysis.py` file contains code to produce a stacked histogram showing the number of messages sent and recieved with a contact each month:

![Sample Graph](/samples/sample_output_graph.png?raw=true)


#### Dependencies
The code is written in Python 2.7.

The parser uses [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/) to do the bulk of the capture from the htm file.

The analysis code uses [matplotlib](http://matplotlib.org/) to produce graphs of message counts. An example graph can be found in the `samples` directory.

[Anaconda Python](https://store.continuum.io/cshop/anaconda/) for scientific computing is a simple and easy way to install all the dependencies for the code, alongside many other useful libraries. It can be downloaded [here](http://continuum.io/downloads).
