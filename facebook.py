import sys
import os
import codecs

import fb_parser
import fb_analysis


# Nasty hack to force utf-8 encoding by default:
reload(sys)
sys.setdefaultencoding('utf8')

# Change stdout to allow printing of unicode characters:
streamWriter = codecs.lookup('utf-8')[-1]
sys.stdout = streamWriter(sys.stdout)

if __name__ == "__main__":
    """Allow the parser to be run from the command line.

       Optionally, the function allows specifying the filename to read in from
       as the first argument."""
    if len(sys.argv) >= 2:
        # If filname passed in and a recognised format, continue:
        if ((".zip" in sys.argv[1]) or (".htm" in sys.argv[1]) or (".pickle" in sys.argv[1])):
            fname = sys.argv[1]
        else:
            # If not a recognised format, stop but allow override:
            print "File is not a .zip file, a .htm file or a pickle file."
            cont = raw_input("Continue anyway? (y/n)")
            if cont == "n":
                sys.exit(-1)
    else:
        # If no argument, attempt to open the default .zip export file:
        fname = "facebook-" + fb_parser.FBMessageParse._MYUSERNAME + ".zip"
    if not os.path.isfile(fname):
        print "File " + fname + " does not exist or could not be found! Abort."
        sys.exit(-1)

    # Some example code to add functionality immediately.

    # Create the parser, and parse the messages file:
    if ".pickle" in fname:
        Facebook = fb_parser.FBMessageParse(fname, load_pickle=True)
    else:
        Facebook = fb_parser.FBMessageParse(fname)
        Facebook.parse_messages()
    # Now find and print the Top 10 Friends:
    print "Top 10 Most Messaged Friends: Total Thread Length"
    top10 = fb_analysis.top_n_people(Facebook.Chat, N=10)
    print top10
    # Output to a csv file:
    Facebook.write_to_csv()
    # Show a graph of the most messaged friend's messages:
    fb_analysis.messages_to_graph(Facebook.Chat, top10[0][0])
