import datetime

from bs4 import BeautifulSoup as bs
import zipfile
import pickle

import codecs
import sys
import os

import fb_chat

reload(sys)
sys.setdefaultencoding('utf8')

streamWriter = codecs.lookup('utf-8')[-1]
sys.stdout = streamWriter(sys.stdout)


class FBMessageParse(object):

    _DATEFORMAT = '%A, %d %B %Y at %H:%M %Z'
    _MYNAME = "My Name"
    _MYUSERNAME = "myusername"

    def __init__(self, fname, load_pickle=False):
        self._UIDPEOPLE = {}
        self._PEOPLEUID = {}
        self._PEOPLEDUPLICATES = {}
        self._UNKNOWNS = []

        self.Chat = None

        self._archive = None
        self._messages_htm = None

        if ".zip" in fname:
            self._archive = zipfile.ZipFile(fname, 'r')
        if self._archive is not None:
            self._messages_htm = self._archive.open('html/messages.htm')
        elif load_pickle:
            self.load_from_pickle(fname)
        else:
            self._messages_htm = open(fname, "r")
        self._read_uid_people()
        self._read_duplicate_list()

    def _close(self):
        if self._archive is not None:
            self._messages_htm = None
            self._archive.close()
        if self._messages_htm is not None:
            self._messages_htm.close()

    def __del__(self):
        self._close()

    def _read_uid_people(self):
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
        namelist = namestr.split(", ")
        for i, name in enumerate(namelist):
            namelist[i] = self._message_author_parse(name)
        if ((self._MYNAME in namelist) and (len(namelist) > 1)):  # You can send yourself messages, so don't delete name if it's the only one.
            namelist.remove(self._MYNAME)                         # Otherwise remove your name from the list.
        return ", ".join(namelist).encode('ascii', 'replace')  # BeutifulSoup works in Unicode, we want ASCII names

    def _message_author_parse(self, name):
        n = name.replace("@facebook.com", "")
        if n in self._UIDPEOPLE:
            name = self._UIDPEOPLE[n]
        if n in self._PEOPLEDUPLICATES:
            name = self._PEOPLEDUPLICATES[n]
        if ((n in name) and (n != name)):  # If n is still the UID, and we still don't have a name:
            self._UNKNOWNS.append(n)      # Add the UID to the UNKNOWN list
        return name.encode('ascii', 'replace')  # BeutifulSoup works in Unicode, we want ASCII names

    def _message_date_parse(self, datestr):
        if "+01" in datestr:
            # BST = 1   # If we want times in UTC, uncomment these lines
            datestr = datestr.replace("+01", "")
        # else:
            # BST = 0
        return datetime.datetime.strptime(datestr, self._DATEFORMAT)  # + datetime.timedelta(hours=BST)

    def _date_unix(self, datetime_date):
        return int((datetime_date - datetime.datetime(1970, 1, 1)).total_seconds())

    def _message_body_parse(self, message_body):
        if message_body is None:
            message_body = ""
        message_body = '<|NEWLINE|>'.join(message_body.splitlines())  # We can't have newline characters in a csv file
#        message_body = message_body.replace(",", "<|COMMA|>")
#        message_body = message_body.replace('"', "<|QUOTE|>")
        message_body = message_body.replace('"', '""')  # Attempt to escape " characters in messages, for csv output
        return message_body

    def print_unknowns(self):
        if self.Chat is None:
            print "The message export file has not been parsed. Run parse_messages()."
            return
        if len(self._UNKNOWNS) == 0:
            return
        self._UNKNOWNS = list(set(self._UNKNOWNS))  # An unordered duplicate removal method
        print "To identify these accounts, try visiting www.facebook.com/[uid] and adding [uid]:[name] to 'uid_people'"
        for uid in self._UNKNOWNS:
            print uid

    def parse_messages(self, group_duplicates=True):
        if self._messages_htm is None:
            print "No archive/message file open. Was data loaded from a pickle file?"
            return
        ###
        soup = bs(self._messages_htm)
        ###
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
        ###
        thread_list = soup.find_all(class_='thread')
        thread_num = 0
        _chat_list = []
        _thread_names = []
        _duplicates_list = []
        for x in thread_list:
            message_list = x.find_all(class_='message')
            _thread_list = []
            total_message_num = len(message_list)
            ###
            message_num = total_message_num
            thread_name = self._thread_name_cleanup(x.contents[0])
            ###
            duplicate_thread = False
            if thread_name in _thread_names:
                duplicate_thread = True
            else:
                _thread_names.append(thread_name)
            ###
            for y in message_list:
                message_author = self._message_author_parse(y.find(class_='user').string)
                message_date = self._message_date_parse(y.find(class_='meta').string)
                message_body = self._message_body_parse(y.next_sibling.string)
                ###
                _thread_list.append(fb_chat.Message(message_author, message_date, message_body, message_num))
                ###
                message_num -= 1
            ###
            thread_num += 1
            ###
            if ((not duplicate_thread) or (not group_duplicates)):
                _chat_list.append(fb_chat.Thread(thread_name.split(", "), _thread_list))
            else:
                for t in _chat_list:
                    if t.people_str == thread_name:
                        _duplicates_list.append(thread_name)
                        t._add_messages(_thread_list)
                        break
        ###
        self.Chat = fb_chat.Chat(self._MYNAME, _chat_list)
        for t in _duplicates_list:
            self.Chat[t]._renumber_messages()

    def write_to_csv(self, filename='messages.csv'):
        with open(filename, "w") as f:
            header_line = '"Thread","Message Number","Message Author","Message Timestamp","Message Body"\n'
            f.write(header_line.encode('utf8'))
            for thread in self.Chat.threads:
                for message in thread.messages:
                    text = '"' + thread.people_str + '",' + str(message)
                    f.write(text.encode('utf8'))

    def dump_to_pickle(self, filename='messages.pickle'):
        with open(filename, "w") as f:
            pickle.dump(self.Chat, f)

    def load_from_pickle(self, filename='messages.pickle'):
        with open(filename, "r") as f:
            self.Chat = pickle.load(f)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if ((".zip" in sys.argv[1]) or (".htm" in sys.argv[1])):
            fname = sys.argv[1]
        else:
            print "File is not a .zip file or a .htm file. Abort."
            sys.exit(-1)
    else:
        fname = "facebook-" + FBMessageParse._MYUSERNAME + ".zip"
    if not os.path.isfile(fname):
        print "File does not exist!"

#    Facebook = FBMessageParse('messages.pickle',load_pickle=True)
    Facebook = FBMessageParse(fname)
    Facebook.parse_messages()
#    print Facebook.Chat.top_n_people(N = 10)
    Facebook.dump_to_pickle()
