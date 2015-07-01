import sys
import codecs
import fb_parser
import ios_parser
import ios_chat


class Merge_Chat_Logs(object):
    """An object to merge the iOS and Facebook Chat objects.

        - The Merge_Chat_Logs object can be treated like a Chat object, and contains
          the original iOS and Facebook Chat objects unchanged, whilst allowing
          the functionality of having combined the two.
        - Contains all the methods and attributes required to allow the fb_analysis
          code to use a Merge_Chat_Logs object as a Chat object. Can consider ios_chat.Chat,
          fb_chat.Chat and facebook_and_sms.Merge_Chat_Logs to be concrete implementations
          of an abstract Chat_Log class; functionality not easily obtainable in Python.
        - When initialising, the Facebook Chat object and the iOS Chat object should
          be passed in as the two arguments."""

    def __init__(self, facebook_Chat, ios_Chat):
        self.Chat = facebook_Chat
        self.Texts = ios_Chat
        self.threads = self.Chat.threads + self.Texts.threads
        self._myname = self.Chat._myname
        self._all_people = self.Chat._all_people.union(self.Texts._all_people)
        self._total_messages = self.Chat._total_messages + self.Texts._total_messages

    def __repr__(self):
        """Set Python's representation of the Chat object."""
        return "<{}'s GROUPED CHAT LOGs: TOTAL_THREADS={} TOTAL_MESSAGES={}>".format(self._myname, len(self), self.Chat._total_messages + self.Texts._total_messages)

    def __len__(self):
        """Return the total number of threads in both Chat objects.

           Allows the len() method to be called on a Merge_Chat_Logs object. This
           could be changed to be the total number of messages, currently stored as
           Merge_Chat_Logs._total_messages()"""
        return len(self.Chat) + len(self.Texts)

    def __getitem__(self, key):
        """Allow accessing Thread objects using Merge_Chat_Logs["Thread Name"].

            - If the thread exists only in one Chat object; that Thread is returned;
              but if a Thread of the same name appears in both, a new Thread object
              combining the two threads is created. Message numbering in this new
              Thread object may be confusing, but functionality remains unchanged.
            - The method will fail silently; None is returned if a key is not present.
              This is different to the more standard rasing of 'KeyError'."""
        if ((key in self.Chat._thread_dict) and (key in self.Texts._thread_dict)):
            return ios_chat.Thread(key, self.Chat[key].messages + self.Texts[key].messages)
        elif key in self.Chat._thread_dict:
            return self.Chat[key]
        elif key in self.Texts._thread_dict:
            return self.Texts[key]
        else:
            return None

    def all_messages(self):
        """Return a date ordered list of all messages.

           The list is all messages contained in both Chat objects, as a list of
           Message objects."""
        return sorted([m for m in self.Chat.all_messages() + self.Texts.all_messages()])

    def all_from(self, name):
        """Return a date ordered list of all messages sent by 'name', from both Chat objects.

           The list returned is a list of Message objects. This is distinct from
           Thread.by(name) since all threads are searched by this method. For all
           messages in one thread from 'name', use Thread.by(name) on the correct Thread."""
        return sorted([m for m in self.Chat.all_from(name) + self.Texts.all_from(name)])

    def sent_before(self, date):
        """Return a date ordered list of all messages sent before specified date, from both Chat objects.

           The function returns a list of Message objects. The 'date' can be a
           datetime.datetime object, or a three to six tuple (YYYY, MM, DD[, HH, MM, SS])."""
        return sorted([m for m in self.Chat.sent_before(date) + self.Texts.sent_before(date)])

    def sent_after(self, date):
        """Return a date ordered list of all messages sent after specified date, from both Chat objects.

           The list returned is a list of Message objects. The 'date' can be a
           datetime.datetime object, or a three to six tuple (YYYY, MM, DD[, HH, MM, SS])."""
        return sorted([m for m in self.Chat.sent_after(date) + self.Texts.sent_after(date)])

    def sent_between(self, start, end=None):
        """Return a date ordered list of all messages sent between specified dates, from both Chat objects.

            - The list returned is a list of Message objects. The 'start' and 'end'
              can be datetime.datetime objects, or a three to six tuple
              (YYYY, MM, DD[, HH, MM, SS]).
            - Not entering an 'end' date is interpreted as all messages sent on
              the day 'start'. Where a time is specified also, a 24 hour period
              beginning at 'start' is used."""
        return sorted([m for m in self.Chat.sent_between(start, end) + self.Texts.sent_between(start, end)])

    def search(self, string, ignore_case=False):
        """Return a date ordered list of all messages containing 'string', from both Chat objects.

           This function searches in all threads, and returns a list of Message
           objects.
            - The function can be made case-insensitive by setting 'ignore_case'
              to True."""
        return sorted([m for m in self.Chat.search(string, ignore_case) + self.Texts.search(string, ignore_case)])


if __name__ == "__main__":
    """The code to get to a Merge_Chat_Logs object, assuming both ios_parser and
       fb_parser have been run and used to pickle their Chat objects with the default
       names."""

    # Nasty hack to force utf-8 encoding by default:
    reload(sys)
    sys.setdefaultencoding('utf8')

    # Change stdout to allow printing of unicode characters:
    streamWriter = codecs.lookup('utf-8')[-1]
    sys.stdout = streamWriter(sys.stdout)

    # To avoid work, assume can load from pickle:
    fb_fname = 'messages.pickle'
    ios_fname = 'sms.pickle'

    Facebook = fb_parser.FBMessageParse(fb_fname)
    SMS = ios_parser.iOSMessageParse(ios_fname)

    All = Merge_Chat_Logs(Facebook.Chat, SMS.Texts)
