import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, num2date
from matplotlib import ticker
import re


# =============================================================================
#                           Graphing Message Counts                           #
# =============================================================================

_FB_GREY = (0.9294, 0.9294, 0.9294)
_FB_BLUE = (0.2314, 0.3490, 0.5961)


def _month_list(d1, d2):
    """Generate a list of months between d1 and d2 inclusive.

       The list includes the months containing d1 and d2, with an extra month
       on the end for the upper limit of a histogram."""
    months = []
    d1 = datetime.datetime(d1.year, d1.month, 1)
    try:
        d2 = datetime.datetime(d2.year, d2.month + 1, 1)
    # If month is 12 (=December), adding one causes error:
    except ValueError:
        # So January of the next year instead
        d2 = datetime.datetime(d2.year + 1, 1, 1)
    # Just generate all months in the required years-range, including unecessary ones
    for y in range(d1.year, d2.year + 1):
        for m in range(1, 13):
            months.append(datetime.datetime(y, m, 1))
    # Then remove extra months
    months = [m for m in months if (d1 <= m <= d2)]
    return months


def messages_to_graph(Chat, name, filename=None, start_date=None, end_date=None, no_gui=False):
    """Create a graph of the number of messages sent between users.

       Produces a graph of messages sent to and recieved from another user. The
       method only works for individuals, not for threads between multiple friends.

       - 'Chat' should be the Chat object to analyse.
       - 'name' should be the name of the user, and so the Thread, to be graphed.
       - If a 'filename' is specified, output to a .png file as well as displaying
         onscreen for viewing.
       - 'start_date' and 'end_date' can be used to narrow the range of dates
         covered; the default is the first message to the last, but specifying dates
         inside this range can be used to narrow down the region considered.
       - To run without displaying a graph onscreen, set 'no_gui' to True. If no filename
         is specified, the function will run but produce no output anywhere."""
    Thread = Chat[name]
    # Sanity check input dates, and fix if necessary (note MUST be one line to avoid reassignment before comparison):
    start_date, end_date = min(start_date, end_date), max(start_date, end_date)
    # If a start date given (which is after the message thread starts), use it:
    if start_date is None:
        d_min = Thread[0].date_time
    else:
        d_min = max(Chat._date_parse(start_date), Thread[0].date_time)
    # If an end date given (which is before the message thread ends), use it:
    if end_date is None:
        d_max = Thread[-1].date_time
    else:
        d_max = min(Chat._date_parse(end_date), Thread[-1].date_time)
    # Divide up into month bins, changing datetime objects to number of days for plotting:
    bins = [date2num(b) for b in _month_list(d_min, d_max)]
    dates_from = [date2num(message.date_time) for message in Thread.by(name)]
    dates_to = [date2num(message.date_time) for message in Thread.by(Chat._myname)]
    # Create the figure, hiding the display if no_gui set:
    if no_gui:
        plt.ioff()
    plt.figure(figsize=(18, 9), dpi=80)
    plt.hist([dates_to, dates_from], bins, histtype='bar', color=[_FB_BLUE, _FB_GREY], label=[Chat._myname, name], stacked=True)
    plt.suptitle("Messages with " + name, size=18)
    plt.ylabel("Number of Messages")
    # Put the tick marks at the rough centre of months by adding 15 days (~ 1/2 a month):
    plt.gca().set_xticks([b + 15 for b in bins])
    # The x labels are unreadbale at angle if more than ~50 of them, put them vertical if so:
    if len(bins) > 50:
        plt.xticks(rotation='vertical')
    else:
        plt.xticks(rotation=30, ha='right')
    # Change the tick marks from useless number of days, to recognisable dates:
    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda numdate, _: num2date(numdate).strftime('%b %Y')))
    # Add some space at either end of the graph (axis in number of days, so -10 days and +5 days):
    plt.xlim([bins[0] - 10, bins[-1] + 5])
    # Place y gridlines beneath the plot:
    plt.gca().yaxis.grid(True)
    plt.gca().set_axisbelow(True)
    # Add the legend at the top, underneath the title but outside the figure:
    plt.legend(frameon=False, bbox_to_anchor=(0.5, 1.05), loc=9, ncol=2, borderaxespad=0)
    # If given a filename, output to file:
    if ((filename is not None) and (type(filename) is str)):
        plt.savefig(filename + '.png', bbox_inches='tight')


# =============================================================================
#                           Word Frequency Analysis                           #
# =============================================================================


def _str_to_word_list(text):
    """Turn a string into a list of words, removing URLs and punctuation.

       - The function takes in a string and returns a list of strings."""
    # Some characters and strings need deleting from messages to separate them into proper words:
    _EXCLUDE = ["'s", "'ll", ".", ",", ":", ";", "!", "?", "*", '"', "-", "+", "^", "_", "~", "(", ")", "[", "]", "/", "\\", "@", "="]
    # Some things need removing, but not deleting as with _EXCLUDE:
    _CHANGE = {"'": "", ":p": "tongueoutsmiley", ":-p": "tongueoutsmiley",
               ":)": "happyfacesmiley", ":-)": "happyfacesmiley", ":/": "awkwardfacesmiley",
               ":-/": "awkwardfacesmiley", "<3": "loveheartsmiley", ":(": "sadfacesmiley",
               ":-(": "sadfacesmiley", ":'(": "cryingfacesmiley", ":d": "grinningfacesmiley",
               ":-d": "grinningfacesmiley", ";)": "winkfacesmiley", ";-)": "winkfacesmiley",
               ":o": "shockedfacesmiley"}
    # Remove URLs with a regular expression, else they mess up when removing punctuation:
    text = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', text)
    # Remove the NEWLINE denoting string, and replace with a space before anything else:
    text = text.replace("<|NEWLINE|>", " ")
    text = text.lower()
    # Change and exclude things:
    for old, new in _CHANGE.items():
        text = text.replace(old, new)
    for ex in _EXCLUDE:
        text = text.replace(ex, " ")
    # A hack to replace all whitespace with one space:
    text = " ".join(text.split())
    # Get rid of non-ASCII characters for simplicity
    text = text.encode('ascii', 'replace')
    # Return a list of words:
    return text.split()


def _message_list_word_list(messages):
    """Take a list of Message objects and return a list of strings.

       The returned list of strings contains all of the words in the messages."""
    word_list = []
    for m in messages:
        word_list.extend(_str_to_word_list(m.text))
    return word_list


def _word_list_to_freq(words, ignore_single_words=False):
    """Take a list of strings, and return a list of (word, word_use_count).

       - The returned list of pairs is sorted in descending order.
       - Passing 'ignore_single_words' will remove any words only used once in
         a message thread."""
    # The order of items in the CHANGE dictionary means changing back isn't quite so simple; just use a second dictionary:
    _CHANGE_BACK = {"tongueoutsmiley": ":P", "happyfacesmiley": ":)", "awkwardfacesmiley": ":/",
                    "loveheartsmiley": "<3", "sadfacesmiley": ":(", "cryingfacesmiley": ":'(",
                    "grinningfacesmiley": ":D", "winkfacesmiley": ";)", "shockedfacesmiley": ":o"}
    # Make a dictionary of words and their total count:
    freq = {x: words.count(x) for x in words}
    # Change the emoticons back to emoticons:
    for new, old in _CHANGE_BACK.items():
        if new in freq:
            freq[old] = freq.pop(new)
    # Convert to a list and sort:
    freq = sorted(freq.items(), key=lambda tup: tup[1], reverse=True)
    # If only want words used more than once, remove those with count <= 1
    if ignore_single_words:
        freq = [f for f in freq if f[1] > 1]
    return freq


def top_word_use(Chat, name, from_me=False, ignore_single_words=False):
    """Work out the most commonly used words by a friend.

       The function returns a list of (word, word_use_count) tuples. For long threads,
       this function will take a long time, due to the analysis being done directly
       in Python, not in a module using the faster C or C++.

       - 'name' is a string of the name of the Thread to consider.
       - 'from_me' is a boolean flag to consider messages sent by you to 'name'
         if True, otherwise messages recieved from 'name' are used, the default.
       - Setting 'ignore_single_words' to True removes words which are only used
         once, which reduces the length of the list returned."""
    if name != Chat._myname:
        if from_me:
            messages = Chat[name].by(Chat._myname)
        else:
            messages = Chat[name].by(name)
    else:
        messages = Chat.all_from(Chat._myname)
    wlist = _message_list_word_list(messages)
    freq = _word_list_to_freq(wlist, ignore_single_words)
    return freq
