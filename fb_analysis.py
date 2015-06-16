import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, num2date
from matplotlib import ticker
import matplotlib
import re

# =============================================================================
#                          Top N Most Messaged People
# =============================================================================


def _update_thread_dict(thread_dict, thread_name, num):
    """Add new entries to count dictionary, dealing with duplicates carefully."""
    if thread_name not in thread_dict:
                thread_dict.update({thread_name: num})
    else:  # Deal with duplicates, otherwise old entries get overwritten:
        thread_dict[thread_name] += num


def top_n_people(Chat, N=-1, count_type="total", groups=False):
    """Return a list of the top N most messaged people.

       The "Top N People" can be judged by one of four criteria. The list
       contains tuples of (name, message count). A negative or zero value for
       N returns the full list, this is the default. The optional argument
       'groups' allows group conversations to be included where this makes
       sense. The 'count_type' argument can be one of four values:
        - "total" - the default. This counts the total number of messages in
          message threads, and sorts by this. Groups can be enabled.
        - "to" - the total number of messages sent in a direct thread by
          the current user: '_myname'. Groups can be enabled.
        - "from" - the total number of messages sent in a direct thread by
          the other person in the thread. If 'groups' is enabled, all messages
          not from '_myname' are counted.
        - "allfrom" - the total number of messages from each individual person
          across all threads. Groups cannot be enabled and will be ignored. This
          will include MYNAME, the current user!"""
    thread_dict = {}
    if count_type is "to":
        for t in Chat.threads:
            num = len(t.by(Chat._myname))
            _update_thread_dict(thread_dict, t.people_str, num)
    elif count_type is "from":
        for t in Chat.threads:
            my_num = len(t.by(Chat._myname))
            tot_num = len(t)
            num = tot_num - my_num
            _update_thread_dict(thread_dict, t.people_str, num)
    elif count_type is "allfrom":
        for p in Chat._all_people:
            num = len(Chat.all_from(p))
            thread_dict.update({p: num})
    else:  # Total messages from each thread
        for t in Chat.threads:
            num = len(t)
            _update_thread_dict(thread_dict, t.people_str, num)
    sorted_list = sorted(thread_dict.items(), key=lambda tup: tup[1], reverse=True)
    top_n = []
    for i, item in enumerate(sorted_list):
        if ((len(top_n) >= N) and (N > 0)):
            return top_n
        if ((len(item[0].split(", ")) == 1) or groups):
            top_n.append((item[0], item[1]))
    return top_n


# =============================================================================
#                           Graphing Message Counts                           #
# =============================================================================

_FB_GREY = (0.9294, 0.9294, 0.9294)
_FB_BLUE = (0.2314, 0.3490, 0.5961)
_BG_COLOUR = (1.0, 1.0, 1.0)
_TEXT_COLOUR = (0.0, 0.0, 0.0)


def _change_matplotlib_colours(text_color=_TEXT_COLOUR, bg_colour=_BG_COLOUR):
    """Change matplotlib default colors for ALL graphs produced in current session.

        - 'text_colour' sets the colour of all text, as well as axes colours and
          axis tick mark colours.
        - 'bg_colour' changes the background and outside fill colour of the plot."""
    matplotlib.rc('figure', facecolor=_BG_COLOUR)
    matplotlib.rc('savefig', facecolor=_BG_COLOUR, edgecolor=_TEXT_COLOUR)
    matplotlib.rc('axes', edgecolor=_TEXT_COLOUR, facecolor=_BG_COLOUR, labelcolor=_TEXT_COLOUR)
    matplotlib.rc('text', color=_TEXT_COLOUR)
    matplotlib.rc('grid', color=_TEXT_COLOUR)
    matplotlib.rc('xtick', color=_TEXT_COLOUR)
    matplotlib.rc('ytick', color=_TEXT_COLOUR)


# Run the colour change code on import of the module:
_change_matplotlib_colours()


# ====== Histogram of Time of Day:


def _hour_list():
    """Generate a list containing hours in day converted to floats."""
    hours_bins = [n / 24.0 for n in range(0, 25)]
    return hours_bins


def _dt_to_decimal_time(datetime):
    """Convert a datetime.datetime object into a fraction of a day float.

       Take the decimal part of the date converted to number of days from 01/01/0001
       and return it. It gives fraction of way through day: the time."""
    datetime_decimal = date2num(datetime)
    time_decimal = datetime_decimal - int(datetime_decimal)
    return time_decimal


def messages_time_graph(Chat, name, filename=None, no_gui=False):
    """Create a graph of the time of day of messages sent between users.

       Produces a histogram of the times of messages sent to and recieved from
       another user. The method only works for individuals, not for threads between
       multiple friends.

       - 'Chat' should be the Chat object to analyse.
       - 'name' should be the name of the user, and so the Thread, to be graphed.
         A special case is when 'name' is the name of the current user, in which
         case the graph of ALL messages the current user has sent is produced.
       - If a 'filename' is specified, output to a .png file as well as displaying
         onscreen for viewing.
       - To run without displaying a graph onscreen, set 'no_gui' to True. If no filename
         is specified with this, the function will run but produce no output anywhere."""
    Thread = Chat[name]
    # Divide up into hourly bins, changing datetime objects to times in range [0,1):
    bins = _hour_list()
    # If looking at graph with other users, get messages to and from:
    if name != Chat._myname:
        times_from = [_dt_to_decimal_time(message.date_time) for message in Thread.by(name)]
        times_to = [_dt_to_decimal_time(message.date_time) for message in Thread.by(Chat._myname)]
        label = [Chat._myname, name]
    else:  # If looking at all messages sent; do things differently:
        times_from = None
        times_to = [_dt_to_decimal_time(message.date_time) for message in Chat.all_from(Chat._myname)]
        label = Chat._myname
    # Create the figure, hiding the display if no_gui set:
    if no_gui:
        plt.ioff()
    plt.figure(figsize=(18, 9), dpi=80)
    plt.hist([times_to, times_from], bins, histtype='bar', color=[_FB_BLUE, _FB_GREY], label=label, stacked=True)
    # Title the graph correctly, and label axes:
    if name != Chat._myname:
        plt.suptitle("Messages with " + name, size=18)
    else:
        plt.suptitle("All Messages Sent", size=18)
    plt.xlabel("Time of Day")
    plt.ylabel("Number of Messages")
    # Move tick marks to centre of hourly bins by adding ~ half an hour (in days)
    plt.gca().set_xticks([b + 0.02 for b in bins])
    # Place tickmarks
    plt.xticks(rotation=0, ha='center')
    # Change the tick marks from useless fraction through day, to recognisable times:
    # To do this use strftime to convert times to string (which needs dates >= 1900),
    # so shift to 1900 (add 693596 days) and take off added half hour (minus 0.02)
    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda numdate, _: num2date(numdate + 693596 - 0.02).strftime('%H:%M')))
    # Add some space at either end of the graph (axis in number of days, so +- 15 mins):
    plt.xlim([bins[0] - 0.01, bins[-1] + 0.01])
    # Place y gridlines beneath the plot:
    plt.gca().yaxis.grid(True)
    plt.gca().set_axisbelow(True)
    # Add the legend at the top, underneath the title but outside the figure:
    plt.legend(frameon=False, bbox_to_anchor=(0.5, 1.05), loc=9, ncol=2, borderaxespad=0)
    # If given a filename, output to file:
    if ((filename is not None) and (type(filename) is str)):
        plt.savefig(filename + '.png', bbox_inches='tight')


# ====== Histogram of Date:


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


def messages_date_graph(Chat, name, filename=None, start_date=None, end_date=None, no_gui=False):
    """Create a graph of the number of messages sent between users.

       Produces a graph of messages sent to and recieved from another user. The
       method only works for individuals, not for threads between multiple friends.

       - 'Chat' should be the Chat object to analyse.
       - 'name' should be the name of the user, and so the Thread, to be graphed.
         A special case is when 'name' is the name of the current user, in which
         case the graph of ALL messages the current user has sent is produced.
       - If a 'filename' is specified, output to a .png file as well as displaying
         onscreen for viewing.
       - 'start_date' and 'end_date' can be used to narrow the range of dates
         covered; the default is the first message to the last, but specifying dates
         inside this range can be used to narrow down the region considered.
       - To run without displaying a graph onscreen, set 'no_gui' to True. If no filename
         is specified with this, the function will run but produce no output anywhere."""
    # Sanity check input dates, and fix if necessary (note MUST be one line to avoid reassignment before comparison):
    if ((start_date is not None) and (end_date is not None)):
        start_date, end_date = min(start_date, end_date), max(start_date, end_date)
    # If looking at graph with other users, get messages to and from:
    if name != Chat._myname:
            Thread = Chat[name]
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
            dates_from = [date2num(message.date_time) for message in Thread.by(name)]
            dates_to = [date2num(message.date_time) for message in Thread.by(Chat._myname)]
            label = [Chat._myname, name]
    # If looking at all messages sent; do things differently:
    else:
        message_list = Chat.all_from(Chat._myname)
        # If a start date given (which is after the message thread starts), use it:
        if start_date is None:
            d_min = message_list[0].date_time
        else:
            d_min = max(Chat._date_parse(start_date), message_list[0].date_time)
        # If an end date given (which is before the message thread ends), use it:
        if end_date is None:
            d_max = message_list[-1].date_time
        else:
            d_max = min(Chat._date_parse(end_date), message_list[-1].date_time)
        dates_from = None
        dates_to = [date2num(message.date_time) for message in message_list]
        label = Chat._myname
    # Divide up into month bins, changing datetime objects to number of days for plotting:
    bins = [date2num(b) for b in _month_list(d_min, d_max)]
    # Create the figure, hiding the display if no_gui set:
    if no_gui:
        plt.ioff()
    plt.figure(figsize=(18, 9), dpi=80)
    plt.hist([dates_to, dates_from], bins, histtype='bar', color=[_FB_BLUE, _FB_GREY], label=label, stacked=True)
    # Title the graph correctly, and label axes:
    if name != Chat._myname:
        plt.suptitle("Messages with " + name, size=18)
    else:
        plt.suptitle("All Messages Sent", size=18)
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


# ====== Pie Chart of Totals:


# Colours from http://www.mulinblog.com/a-color-palette-optimized-for-data-visualization/
_COLOURS = ['#5DA5DA', '#FAA43A', '#60BD68', '#F17CB0', '#B2912F', '#B276B2', '#DECF3F', '#F15854']


def _make_labels_wrap(labels):
    """Break labels which contain more than one name into multiple lines."""
    for i, l in enumerate(labels):
        if len(l) > 25:
            # Split lines at ", " and rejoin with newline.
            labels[i] = '\n'.join(l.split(", "))
    return labels


def messages_pie_chart(Chat, N=10, filename=None, count_type="total", groups=False,
                       no_gui=False, percentages=True):
    """Create a pie chart of the number of messages exchanged with friends.

       The graph shows the most messaged friends sorted using the top_n_people()
       code. The graph also shows percentage sizes of wedges, though this can be disabled.
        - 'Chat' should be the Chat object to analyse.
        - 'N' should be how many people to show explicitly; all others are grouped
          together in a final chunk.
        - If a 'filename' is specified, output to a .png file as well as displaying
          onscreen for viewing.
        - The 'count_type' argument is passed to top_n_people() and so one of the
          four valid counts can be used.
        - Setting 'groups' to True will include message threads with groups where
          appropriate.
        - To run without displaying a graph onscreen, set 'no_gui' to True. If no filename
          is specified with this, the function will run but produce no output anywhere.
        - The percentages on the graph can be removed by setting 'percentages' to
          False."""
    # The title of the graph depends on the count_type:
    _title_dict = {"total": "Total Lengths of Message Threads", "allfrom": "Total Number of Messages Recieved",
                   "from": "Number of Messages Recieved from People in Personal Threads",
                   "to": "Number of Messages Sent to People in Personal Threads"}
    # The data to plot:
    thread_counts = top_n_people(Chat, count_type=count_type, groups=groups)
    # Set up useful lists and counts:
    names = []
    counts = []
    other_count = 0
    colours = []
    # Run through the data, adding it to the correct list. If not in N, add to Other:
    for n, t in enumerate(thread_counts):
        if n < N:
            names.append(t[0])
            counts.append(t[1])
            colours.append(_COLOURS[n % len(_COLOURS)])
        else:
            other_count += t[1]
    # Add an "Others" section in dark grey using the other_count:
    names.append("Others")
    counts.append(other_count)
    colours.append('#4D4D4D')
    # If long names, wrap them:
    _make_labels_wrap(names)
    # Create the figure, hiding the display if no_gui set:
    if no_gui:
        plt.ioff()
    plt.figure(figsize=(18, 9), dpi=80)
    # We want the edges of the wedges in the chart to be white for aesthetics:
    plt.rcParams['patch.edgecolor'] = 'white'
    # Plot percentage counts on the figure:
    if percentages:
        pct = '%1.1f%%'
    else:
        pct = None
    # Make the plot, starting at the top (90 degrees from horizontal) and percentages outside (pctdist > 1)
    plt.pie(counts, colors=colours, autopct=pct, pctdistance=1.1, startangle=90, counterclock=False)
    # Put the right title on the graph:
    plt.suptitle(_title_dict[count_type], size=18)
    # And make it circular:
    plt.axis('equal')
    # Add the legend:
    plt.legend(labels=names, frameon=False, labelspacing=1, loc="center", bbox_to_anchor=[0, 0.5])
    # If given a filename, output to file:
    if ((filename is not None) and (type(filename) is str)):
        plt.savefig(filename + '.png', bbox_inches='tight')
    # To get white outlines, we changed default. Fix this:
    plt.rcParams['patch.edgecolor'] = _TEXT_COLOUR


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
       THIS FUNCTION WILL TAKE A VERY LONG TIME, due to the analysis being done
       directly in Python, not in a module using the faster C or C++.

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
