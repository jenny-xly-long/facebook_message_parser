import datetime
import sys
from bs4 import BeautifulSoup as bs
import zipfile
import pickle
import fb_chat


class FBMessageParse(object):
    """An object to encapsulate all the methods required to parse messages.htm.

       These include methods to initialise, save and load a fb_chat.Chat object,
       which contains a Pythonic representation of Facebook Message history.
        - Can read in messages from the .zip archive exported from Facebook, or
          the .htm file contained in the archive.
        - Can dump the Chat object to a pickle file and load it again in another
          session: use dump_to_pickle() and load_from_pickle().
        - Can export messages to csv format: use write_to_csv()
        - Using a 'uid_people' file, can turn unrecognised nnnnnnn@facebook.com identifiers
          into names. Lines should be '[uid]:[name]'. See the print_unknowns() function.
        - Allows customised renaming of contacts using a 'duplicates' file. In a similar
          way to the 'uid_people' file; add lines containing '[old name]:[new name]' to
          a file called 'duplicates' for the process to occur on the next read in from
          zip or htm."""

    _DATEFORMAT = '%A, %d %B %Y at %H:%M %Z'
    _MYNAME = "My Name"
    _MYUSERNAME = "myusername"

    def __init__(self, fname, load_pickle=False):
        self._UIDPEOPLE = {}
        self._PEOPLEUID = {}
        self._PEOPLEDUPLICATES = {}
        self._UNKNOWNS = []
        #
        self.Chat = None
        #
        self._archive = None
        self._messages_htm = None
        # Open either the .zip and contained htm, the pickle file, or another file:
        if ".zip" in fname:
            self._archive = zipfile.ZipFile(fname, 'r')
        if self._archive is not None:
            self._messages_htm = self._archive.open('html/messages.htm')
        elif load_pickle:
            self.load_from_pickle(fname)
        else:
            self._messages_htm = open(fname, "r")
        #
        self._read_uid_people()
        self._read_duplicate_list()

    def _close(self):
        """Close any open files before deletion. Do not call manually."""
        if self._archive is not None:
            self._messages_htm = None
            self._archive.close()
        if self._messages_htm is not None:
            self._messages_htm.close()

    def __del__(self):
        """Ensure _close() is called on deletion."""
        self._close()

    def _read_uid_people(self):
        """Read in the 'uid_people' file and add line entries to dictionaries.

           Called automatically; do not call manually. Read in the 'uid_people'
           file and add line entries to the dictionaries used to translate between
           UID and Name, and vice versa.
            - Lines should be formatted '[uid]:[name]'.
            - Ill-formatted lines are ignored, and the file does not have to be present
              for the code to function: unrecognised UIDs are left unchanged."""
        try:
            with open('uid_people') as f:
                lines = [line.rstrip('\n') for line in f]
                for line in lines:
                    try:
                        key, value = line.split(":")
                        self._UIDPEOPLE.update({key: value})
                        self._PEOPLEUID.update({value: key})
                    except ValueError:
                        pass
        except IOError:
            pass

    def _read_duplicate_list(self):
        """Read in the 'duplicates' file and add line entries to the dictionary.

           Called automatically; do not call manually. Read in the 'duplicates'
           file and add line entries to the dictionary used to replace names.
           Useful for people who have changed their Facebook name to a nickname,
           or appear in the Chat logs with two versions of their name.
            - Lines should be formatted '[old name]:[new name]'.
            - Ill-formatted lines are ignored, and the file does not have to be
              present for the code to function: unrecognised names are left unchanged."""
        try:
            with open('duplicates') as f:
                lines = [line.rstrip('\n') for line in f]
                for line in lines:
                    try:
                        key, value = line.split(":")
                        self._PEOPLEDUPLICATES.update({key: value})
                    except ValueError:
                        pass
        except IOError:
            pass

    def _thread_name_cleanup(self, namestr):
        """Parse the thread's name.

           Change any message author names and remove the name of the Chat owner
           (_MYNAME) from the name unless messages are sent to oneself."""
        namelist = sorted(namestr.split(", "))
        for i, name in enumerate(namelist):
            namelist[i] = self._message_author_parse(name)
        if ((self._MYNAME in namelist) and (len(namelist) > 1)):  # You can send yourself messages, so don't delete name if it's the only one.
            namelist.remove(self._MYNAME)                         # Otherwise remove your name from the list.
        return ", ".join(namelist).encode('ascii', 'replace')  # BeutifulSoup works in Unicode, do we want ASCII names?

    def _message_author_parse(self, name):
        """Tidy up the name of the sender of a message.

           If the name is a UID email address, use the UID dictionary to replace
           their name if possible. If the name is a duplicate (or to be renamed)
           then rename. Any UIDs which remain are added to a list to facilitate
           populating a 'uid_people' file: see print_unknowns()."""
        n = name.replace("@facebook.com", "")
        if n in self._UIDPEOPLE:
            name = self._UIDPEOPLE[n]
        if n in self._PEOPLEDUPLICATES:
            name = self._PEOPLEDUPLICATES[n]
        if ((n in name) and (n != name)):  # If n is still the UID, and we still don't have a name:
            self._UNKNOWNS.append(n)      # Add the UID to the UNKNOWN list
        return name.encode('ascii', 'replace')  # BeutifulSoup works in Unicode, do we want ASCII names?

    def _message_date_parse(self, datestr):
        """Turn the datestamp on the message into a datetime object.

           UK based datestamps have +01 for BST; other locales may require
           customised versions of this code."""
        if "+01" in datestr:
            # BST = 1   # If we want times in UTC, uncomment these lines
            datestr = datestr.replace("+01", "")
        # else:
            # BST = 0
        return datetime.datetime.strptime(datestr, self._DATEFORMAT)  # + datetime.timedelta(hours=BST)

    def _date_unix(self, datetime_date):
        """Turn a datetime.datetime object into a UNIX time int."""
        return int((datetime_date - datetime.datetime(1970, 1, 1)).total_seconds())

    def _message_body_parse(self, message_body):
        """Tidy up the message body itself.

           This turns newline characters into a unique custom string which can
           be replaced after export if necessary. Quote marks are also escaped,
           to allow the use of quotes and commas in messages whilst allowing
           export to csv. Those two lines can be removed if desired."""
        if message_body is None:
            message_body = ""
        message_body = '<|NEWLINE|>'.join(message_body.splitlines())  # We can't have newline characters in a csv file
        message_body = message_body.replace('"', '""')  # Attempt to escape " characters in messages, for csv output
        return message_body

    def print_unknowns(self):
        """Print out any UIDs of people not recognised by the code.

           Prints lines containing unrecognised UIDs, along with instructions on
           how to find names for these people and how to add the names to the
           'uid_people' file."""
        if self.Chat is None:
            print "The message export file has not been parsed. Run parse_messages()."
            return
        if len(self._UNKNOWNS) == 0:
            return
        self._UNKNOWNS = list(set(self._UNKNOWNS))  # An unordered duplicate removal method
        print "To identify these accounts, try visiting www.facebook.com/[uid] and adding '[uid]:[name]' to a file in the current directory named 'uid_people'"
        for uid in self._UNKNOWNS:
            print uid

    def parse_messages(self, group_duplicates=True):
        """Take the loaded zip file or htm file and create a Chat object.

           Takes the messages.htm file and reads in the messages using
           BeautifulSoup to parse the html data. Creates the Chat object, which
           can be used independently and accessed as the FBMessageParse.Chat object.
            - Optional argument 'group_duplicates' groups together Threads containing
              the same participants. Message Threads over 10,000 messages long are
              split by Facebook for export: this can help group them. True by default.
            - Contains code to verify that the file being examined is in fact a
              Facebook Messages export, though it allows manual override."""
        # Check we have a htm file open to import from:
        if self._messages_htm is None:
            print "No archive/message file open. Was data loaded from a pickle file?"
            return
        #
        soup = bs(self._messages_htm)
        # Verify that we're parsing a Facebook Message export and _MYNAME is right:
        check_header = self._MYNAME + " - Messages"
        try:
            actual_header = soup.html.head.title.string
        except AttributeError:
            actual_header = None
        if ((actual_header is None) or (check_header != actual_header)):
            print "The title of the htm document does not match that expected:"
            print '"' + check_header + '"'
            print "Is the file a message export? Is the user's name correct?"
            cont = raw_input("Continue anyway? (y/n)")
            if cont == "n":
                sys.exit(-1)
        # Set up some important lists:
        thread_list = soup.find_all(class_='thread')
        thread_num = 0
        _chat_list = []
        _thread_names = []
        _duplicates_list = []
        # Start going through the threads:
        for t in thread_list:
            message_list = t.find_all(class_='message')
            _thread_list = []
            total_message_num = len(message_list)
            #
            message_num = total_message_num
            thread_name = self._thread_name_cleanup(t.contents[0])
            # Work out if the thread is a duplicate:
            duplicate_thread = False
            if thread_name in _thread_names:
                duplicate_thread = True
            else:
                _thread_names.append(thread_name)
            # For each message, sort Author, Date and Body then create Message object:
            for m in message_list:
                message_author = self._message_author_parse(m.find(class_='user').string)
                message_date = self._message_date_parse(m.find(class_='meta').string)
                message_body = self._message_body_parse(m.next_sibling.string)
                #
                _thread_list.append(fb_chat.Message(thread_name, message_author, message_date, message_body, message_num))
                #
                message_num -= 1
            #
            thread_num += 1
            # If we're grouping duplicated threads, deal with them now:
            if ((not duplicate_thread) or (not group_duplicates)):
                _chat_list.append(fb_chat.Thread(thread_name.split(", "), _thread_list))
            else:
                for t in _chat_list:
                    if t.people_str == thread_name:
                        _duplicates_list.append(thread_name)
                        t._add_messages(_thread_list)
                        break
        # Create the Chat object, set and return it:
        self.Chat = fb_chat.Chat(self._MYNAME, _chat_list)
        for t in _duplicates_list:
            self.Chat[t]._renumber_messages()  # If we've grouped them, the messages need renumbering.
        return self.Chat

    def write_to_csv(self, filename='messages.csv', chronological=False):
        """Export all messages to csv format.

           The filename can be specified as an optional argument. If 'chronological'
           is True, messages are printed in date order, otherwise they are printed
           grouped in Threads sorted by total thread length."""
        with open(filename, "w") as f:
            header_line = '"Thread","Message Number","Message Author","Message Timestamp","Message Body"\n'
            f.write(header_line.encode('utf8'))
            if chronological:
                for message in self.Chat.all_messages():
                    text = str(message)
                    f.write(text.encode('utf8'))
            else:
                for thread in self.Chat.threads:
                    for message in thread.messages:
                        text = str(message)
                        f.write(text.encode('utf8'))

    def dump_to_pickle(self, filename='messages.pickle'):
        """Serialise the Chat object to a pickle file.

           The pickle file can be used to restore the Chat object in another
           session without re-importing the zip or htm file. Load either using
           load_from_pickle(), or in another program using Pickle's standard load()
           command."""
        with open(filename, "w") as f:
            pickle.dump(self.Chat, f)

    def load_from_pickle(self, filename='messages.pickle'):
        """Read in the pickle file, optionally from a specified filename.

           The function sets the internal Chat object and returns the Chat object.
           Provided mainly as an example, since the parser's main aim to to read
           in from zip or htm, and to output csv or the Chat object."""
        with open(filename, "r") as f:
            self.Chat = pickle.load(f)
        return self.Chat
