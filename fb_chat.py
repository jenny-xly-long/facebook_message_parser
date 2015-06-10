class Chat(object):
    """Contains a list of Threads"""

    def __init__(self, threads):
        self.threads = threads
        self.thread_dict = {", ".join(thread.people): thread for thread in self.threads}
        self._total_messages = 0
        for thread in self.threads:
            self._total_messages += len(thread)
        

    def __getitem__(self, key):
        if type(key) is int: return self.threads[key]
        elif type(key) is str: return self.thread_dict[key]

    def __repr__(self):
        return '<Chat: total_threads={} total_messages={}>'.format(len(self.threads), self._total_messages)

    def __len__(self):
        return len(self.threads)

    # returns a date-sorted list of messages sent by "name"
    def all_from(self, name):
        return sorted([msg for thread in self.threads if name in thread.people for msg in thread.by(name)])

    def sent_before(self, date):
        return [msg for thread in self.threads for msg in thread.sent_before(date)]

    def sent_after(self, date):
        return [msg for thread in self.threads for msg in thread.sent_after(date)]

    def sent_between(self,beg,end):
        return [msg for thread in self.threads for msg in thread.sent_between(beg,end)]


class Thread(object):
    """Contains a list of people included, and messages """

    def __init__(self,people,messages):
        self.people = people
        self.messages = sorted(messages)

    def __getitem__(self, key): return self.messages[key]

    def __repr__(self):
        return '<Thread: people={}, thread_length={}>'.\
            format(self.people, len(self.messages))

    def __str__(self): return '{}\n{}\n'.format(self.people, self.messages)

    def __len__(self): return len(self.messages)

    def _add_messages(self, new_messages):
        self.messages.extend(new_messages)
        self.messages = sorted(self.messages)

    def _renumber_messages(self):
        i = 1
        for message in self.messages:
            message._num = i
            i += 1

    def by(self, name):
        return [msg for msg in self.messages if msg.sent_by(name)]

    def sent_before(self, date):
        return [msg for msg in self.messages if msg.sent_before(date)]

    def sent_after(self, date):
        return [msg for msg in self.messages if msg.sent_after(date)]

    def sent_between(self, beg, end):
        return [msg for msg in self.messages if msg.sent_between(beg, end)]


class Message(object):
    """Contains the message text, sender, and date/time"""

    def __init__(self, sender, date_time, text, num):
        self.sender = sender
        self.date_time = date_time
        self.text = text
        self._num = num

    def __repr__(self):
        return '<Message: number={} date_time={} author={} message_body={}'.format(self._num,
            self.date_time, self.sender, self.text)

    def __str__(self):
        return '{}\n{}\n{}\n'.format(self.sender, self.date_time, self.text)

    def __lt__(self, message):
        if self.date_time == message.date_time:
            if abs(self._num - message._num)>9000:    # If dates equal, but numbers miles apart
                return False;  # MUST be where two 10000 groups join: larger number actually smaller here!
            else:
                return self._num < message._num
        return self.sent_before(message.date_time)

    def __gt__(self, message):
        if self.date_time == message.date_time:
            if abs(self._num - message._num)>9000:    # If dates equal, but numbers miles apart
                return True  # MUST be where two 10000 groups join: smaller number actually larger here!
            else:
                return self._num > message._num
        return self.sent_after(message.date_time)

    def __eq__(self, message):
        return self._num == message._num

    def sent_by(self, name):
        return self.sender == name

    def sent_before(self,date):
        return self.date_time < date

    def sent_after(self,date):
        return self.date_time > date

    def sent_between(self, beg, end):
        return beg < self.date_time < end
