import datetime


class Chat(object):
    """An object to encapsulate the entire Facebook Message history.

        - Contains a list of Thread objects, which can be accessed using item
          accessing Chat["Thread Name"] style.
        - When initialising, 'myname' should be the name of the user, and 'threads'
          should be a list of Thread objects.
        - Provides useful functions for accessing messages."""

    def __init__(self, myname, threads):
        self.threads = sorted(threads, key=len, reverse=True)
        self._thread_dict = {", ".join(thread.people): thread for thread in self.threads}
        self._total_messages = len(self.all_messages())
        self._myname = myname
        self._all_people = {myname}
        for thread in self.threads:
            self._all_people.update(thread.people)

    def __getitem__(self, key):
        """Allows accessing Thread objects in the threads list using Chat["Thread Name"]
           or Chat[n] notation."""
        if type(key) is int:
            return self.threads[key]
        elif type(key) is str:
            return self._thread_dict[key]

    def __repr__(self):
        """Set Python's representation of the Chat object."""
        return "<{}'s CHAT LOG: TOTAL_THREADS={} TOTAL_MESSAGES={}>".format(self._myname, len(self.threads), self._total_messages)

    def __len__(self):
        """Allow len() called on the Chat obejct to return the total number of
           threads. This could be changed to be the total number of messages,
           currently stored as Chat._total_messages()"""
        return len(self.threads)

    def _date_parse(self, date):
        """Allow dates to be entered as integer tuples (YYYY, MM, DD[, HH, MM])
           as well as entered as datetime.datetime objects. The Year, Month and
           Day are compulsory, the Hours and Minutes optional. May cause exceptions
           if poorly formatted tuples are used."""
        if type(date) is datetime.datetime:
            return date
        else:
            return datetime.datetime(*date)

    def _recount_messages(self):
        """Update the count of total messages; since Thread objects can be extended
           dynamically, this may prove necessary."""
        self._total_messages = len(self.all_messages())

    def all_messages(self):
        """Returns a date ordered list of all messages contained in the Chat object,
           as a list of Message objects."""
        return sorted([message for thread in self.threads for message in thread.messages])

    def all_from(self, name):
        """Returns a date ordered list of all messages sent by 'name', as a list
           of Message objects. This is distinct from Thread.by(name) since all
           threads are searched by this method. For all messages in one thread
           from 'name', use Thread.by(name) on the correct Thread."""
        return sorted([message for thread in self.threads for message in thread.by(name)])

    def sent_before(self, date):
        """Returns a date ordered list of all messages sent before the date specified,
           as a list of Message objects. The 'date' can be a datetime.datetime
           object, or a three or five tuple (YYYY, MM, DD[, HH, MM])."""
        date = self._date_parse(date)
        return sorted([message for thread in self.threads for message in thread.sent_before(date)])

    def sent_after(self, date):
        """Returns a date ordered list of all messages sent after the date specified,
           as a list of Message objects. The 'date' can be a datetime.datetime
           object, or a three or five tuple (YYYY, MM, DD[, HH, MM])."""
        date = self._date_parse(date)
        return sorted([message for thread in self.threads for message in thread.sent_after(date)])

    def sent_between(self, start, end):
        """Returns a date ordered list of all messages sent between the dates
           specified, as a list of Message objects. The 'start' and 'end' can be
           datetime.datetime objects, or a three or five tuple (YYYY, MM, DD[, HH, MM])."""
        start = self._date_parse(start)
        end = self._date_parse(end)
        return sorted([message for thread in self.threads for message in thread.sent_between(start, end)])

    def top_n_people(self, N=-1, count_type="total", groups=False):
        """Return a list of the top N most messaged people, judged by one of four
           criteria. The list contains tuples of (name, message count). A negative
           or zero value for N returns the full list, this is the default. The optional
           argument 'groups' allows group conversations to be included where this
           makes sense. The 'count_type' argument can be one of four values:
            - "total" - the default. This counts the total number of messages in
              message threads, and sorts by this. Groups can be enabled.
            - "to" - the total number of messages sent in a direct thread by
              the current user: '_myname'. Groups can be enabled.
            - "from" - the total number of messages sent in a direct thread by
              the other person in the thread. If 'groups' is enabled, all messages
              not from '_myname' are counted.
            - "allfrom" - the total number of messages from each individual person
              across all threads. Groups cannot be enabled and will be ignored."""
        thread_dict = {}
        if count_type is "to":
            for t in self.threads:
                num = len(t.by(self._myname))
                if t.people_str not in thread_dict:  # Deal with duplicates, otherwise old entries get overwritten
                    thread_dict.update({t.people_str: num})
                else:
                    thread_dict[t.people_str] += num
        elif count_type is "from":
            for t in self.threads:
                my_num = len(t.by(self._myname))
                tot_num = len(t)
                num = tot_num - my_num
                if t.people_str not in thread_dict:  # Deal with duplicates, otherwise old entries get overwritten
                    thread_dict.update({t.people_str: num})
                else:
                    thread_dict[t.people_str] += num
        elif count_type is "allfrom":
            for p in self._all_people:
                num = len(self.all_from(p))
                thread_dict.update({p: num})
        else:  # Total messages from each thread
            for t in self.threads:
                num = len(t)
                if t.people_str not in thread_dict:  # Deal with duplicates, otherwise old entries get overwritten
                    thread_dict.update({t.people_str: num})
                else:
                    thread_dict[t.people_str] += num
        sorted_list = sorted(thread_dict.items(), key=lambda tup: tup[1], reverse=True)
        top_n = []
        for i, item in enumerate(sorted_list):
            if ((len(top_n) >= N) and (N > 0)):
                return top_n
            if ((len(item[0].split(", ")) == 1) or groups):
                top_n.append((item[0], item[1]))
        return top_n

    def search(self, string, ignore_case=False):
        """Returns a date ordered list of all messages in the thread containing
           'string', as a list of Message objects."""
        return sorted([message for thread in self.threads for message in thread.search(string, ignore_case)])


class Thread(object):
    """An object to encapsulate a Facebook Message thread.

        - Contains a list of participants, a string form of the list and a list
          of messages in the thread as Message objects.
        - When initialising, 'people' should be a list of strings containing the
          names of the participants and 'messages' should be a list of Message
          objects."""

    def __init__(self, people, messages):
        self.people = people
        self.people_str = ", ".join(self.people)
        self.messages = sorted(messages)

    def __getitem__(self, key):
        """Allows accessing Message objects in the messages list using Thread[n].
           Beware out by one errors!"""
        return self.messages[key]

    def __repr__(self):
        """Set Python's representation of the Thread object."""
        return '<THREAD: PEOPLE={}, MESSAGE_COUNT={}>'.format(self.people_str, len(self.messages))

    def __len__(self):
        """Allow len() called on the Thread obejct to return the total number of
           messages in the thread."""
        return len(self.messages)

    def _date_parse(self, date):
        """Allow dates to be entered as integer tuples (YYYY, MM, DD[, HH, MM])
           as well as entered as datetime.datetime objects. The Year, Month and
           Day are compulsory, the Hours and Minutes optional. May cause exceptions
           if poorly formatted tuples are used."""
        if type(date) is datetime.datetime:
            return date
        else:
            return datetime.datetime(*date)  # Expand the tuple and allow datetime to process it

    def _add_messages(self, new_messages):
        """Allows adding messages to an already created Thread object; useful for
           merging duplicate threads together."""
        self.messages.extend(new_messages)
        self.messages = sorted(self.messages)

    def _renumber_messages(self):
        """Renumbers all messages in the 'messages' list; they are sorted after
           being added; but if messages are added using _add_messages() then the
           numbering may be incorrect. This function fixes that."""
        i = 1
        for message in self.messages:
            message._num = i
            i += 1

    def by(self, name):
        """Returns a date ordered list of all messages sent by 'name', as a list
           of Message objects."""
        return [message for message in self.messages if message.sent_by(name)]

    def sent_before(self, date):
        """Returns a date ordered list of all messages sent before the date specified,
           as a list of Message objects. The 'date' can be a datetime.datetime
           object, or a three or five tuple (YYYY, MM, DD[, HH, MM])."""
        date = self._date_parse(date)
        return [message for message in self.messages if message.sent_before(date)]

    def sent_after(self, date):
        """Returns a date ordered list of all messages sent after the date specified,
           as a list of Message objects. The 'date' can be a datetime.datetime
           object, or a three or five tuple (YYYY, MM, DD[, HH, MM])."""
        date = self._date_parse(date)
        return [message for message in self.messages if message.sent_after(date)]

    def sent_between(self, start, end):
        """Returns a date ordered list of all messages sent between the dates
           specified, as a list of Message objects. The 'start' and 'end' can be
           datetime.datetime objects, or a three or five tuple (YYYY, MM, DD[, HH, MM])."""
        start = self._date_parse(start)
        end = self._date_parse(end)
        return [message for message in self.messages if message.sent_between(start, end)]

    def search(self, string, ignore_case=False):
        """Returns a date ordered list of all messages in the thread containing
           'string', as a list of Message objects."""
        return sorted([message for message in self.messages if message.contains(string, ignore_case)])


class Message(object):
    """An object to encapsulate a Facebook Message.

        - Contains a string of the author's name, the timestamp, number in the thread
          and the body of the message.
        - When initialising, thread_name' should be the containing Thread.people_str,
          'author' should be string containing the message sender's name, 'date_time'
          should be a datetime.datetime object, 'text' should be the content of
          the message and 'num' should be the number of the message in the thread."""

    def __init__(self, thread, author, date_time, text, num):
        self.thread_name = thread
        self.author = author
        self.date_time = date_time
        self.text = text
        self._num = num

    def __repr__(self):
        """Set Python's representation of the Message object."""
        return '<MESSAGE: THREAD={} NUMBER={} TIMESTAMP={} AUTHOR={} MESSAGE="{}">'.\
            format(self.thread_name, self._num, self.date_time, self.author, self.text)

    def __str__(self):
        """The string form of a Message is the format required for csv output."""
        out = '"' + self.thread_name + '","' + str(self._num) + '","' + self.author + '","' + str(self.date_time) + '","' + self.text + '"\n'
        return out

    def __lt__(self, message):
        """Allow sorting of messages by implementing the less than operator.
           Sorting is by date, unless two messages were sent at the same time,
           in which case message number is used to resolve conflicts. This number
           ordering holds fine for messages in single threads, but offers no real
           objective order outside a thread."""
        if self.date_time == message.date_time:
            if abs(self._num - message._num) > 9000:    # If dates equal, but numbers miles apart
                return False  # MUST be where two 10000 groups join: larger number actually smaller here!
            else:
                return self._num < message._num
        return self.sent_before(message.date_time)

    def __gt__(self, message):
        """Allow sorting of messages by implementing the greater than operator.
           Sorting is by date, unless two messages were sent at the same time,
           in which case message number is used to resolve conflicts. This number
           ordering holds fine for messages in single threads, but offers no real
           objective order outside a thread."""
        if self.date_time == message.date_time:
            if abs(self._num - message._num) > 9000:    # If dates equal, but numbers miles apart
                return True  # MUST be where two 10000 groups join: smaller number actually larger here!
            else:
                return self._num > message._num
        return self.sent_after(message.date_time)

    def __eq__(self, message):
        """Messages are equal if their number, date, author and text are the same."""
        equal = (self._num == message._num) and (self.author == message.author)
        equal = equal and (self.date_time == message.date_time) and (self.text == message.text)
        return equal

    def _date_parse(self, date):
        """Allow dates to be entered as integer tuples (YYYY, MM, DD[, HH, MM])
           as well as entered as datetime.datetime objects. The Year, Month and
           Day are compulsory, the Hours and Minutes optional. May cause exceptions
           if poorly formatted tuples are used."""
        if type(date) is datetime.datetime:
            return date
        else:
            return datetime.datetime(*date)

    def sent_by(self, name):
        """Returns True if the message was sent by 'name'."""
        return self.author == name

    def sent_before(self, date):
        """Returns True if the message was sent before the date specified. The
           'date' can be a datetime.datetime object, or a three or five tuple
           (YYYY, MM, DD[, HH, MM])."""
        date = self._date_parse(date)
        return self.date_time < date

    def sent_after(self, date):
        """Returns True if the message was sent after the date specified. The
           'date' can be a datetime.datetime object, or a three or five tuple
           (YYYY, MM, DD[, HH, MM])."""
        date = self._date_parse(date)
        return self.date_time > date

    def sent_between(self, start, end):
        """Returns True if the message was sent between the dates specified by 'start'
           and 'end'. The 'start' and 'end' can be datetime.datetime objects, or
           a three or five tuple (YYYY, MM, DD[, HH, MM]). The start and end times
           are inclusive since this is simplest."""
        start = self._date_parse(start)
        end = self._date_parse(end)
        return start <= self.date_time <= end

    def contains(self, search_string, ignore_case=False):
        """Returns True if 'search_string' is contained in the message text."""
        if ignore_case:
            return search_string.lower() in self.text.lower()
        else:
            return search_string in self.text
