import datetime


class Chat(object):
    """Contains a list of Threads"""

    def __init__(self, myname, threads):
        self.threads = sorted(threads, key=len, reverse=True)
        self.thread_dict = {", ".join(thread.people): thread for thread in self.threads}
        self._total_messages = 0
        self._myname = myname
        self._all_people = {myname}
        for thread in self.threads:
            self._total_messages += len(thread)
            self._all_people.update(thread.people)

    def __getitem__(self, key):
        if type(key) is int: return self.threads[key]
        elif type(key) is str: return self.thread_dict[key]

    def __repr__(self):
        return "<{}'s CHAT LOG: TOTAL_THREADS={} TOTAL_MESSAGES={}>".format(self._myname, len(self.threads), self._total_messages)

    def __len__(self):
        return len(self.threads)

    def _date_parse(self, date):
        if type(date) is datetime.datetime:
            return date
        else:
            return datetime.datetime(*date)

    def _recount_messages(self):
        self._total_messages = len(self.all_messages())

    def all_messages(self):
        return sorted([msg for thread in self.threads for msg in thread.messages])

    # returns a date-sorted list of messages sent by "name"
    def all_from(self, name):
        return sorted([msg for thread in self.threads if name in thread.people for msg in thread.by(name)])

    def sent_before(self, date):
        date = self._date_parse(date)
        return [msg for thread in self.threads for msg in thread.sent_before(date)]

    def sent_after(self, date):
        date = self._date_parse(date)
        return [msg for thread in self.threads for msg in thread.sent_after(date)]

    def sent_between(self,beg,end):
        beg = self._date_parse(beg)
        end = self._date_parse(end)
        return [msg for thread in self.threads for msg in thread.sent_between(beg,end)]

    def top_n_people(self, N=-1, count_type="total", groups=False):
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


class Thread(object):
    """Contains a list of people included, and messages """

    def __init__(self,people,messages):
        self.people = people
        self.people_str = ", ".join(self.people)
        self.messages = sorted(messages)

    def __getitem__(self, key): return self.messages[key]

    def __repr__(self):
        return '<THREAD: PEOPLE={}, MESSAGE_COUNT={}>'.\
            format(self.people_str, len(self.messages))

    def __str__(self):
        return '{}\n{}\n'.format(self.people, self.messages)

    def __len__(self):
        return len(self.messages)

    def _date_parse(self, date):
        if type(date) is datetime.datetime:
            return date
        else:
            return datetime.datetime(*date)

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
        date = self._date_parse(date)
        return [msg for msg in self.messages if msg.sent_before(date)]

    def sent_after(self, date):
        date = self._date_parse(date)
        return [msg for msg in self.messages if msg.sent_after(date)]

    def sent_between(self, beg, end):
        beg = self._date_parse(beg)
        end = self._date_parse(end)
        return [msg for msg in self.messages if msg.sent_between(beg, end)]


class Message(object):
    """Contains the message text, author, and date/time"""

    def __init__(self, author, date_time, text, num):
        self.author = author
        self.date_time = date_time
        self.text = text
        self._num = num

    def __repr__(self):
        return '<MESSAGE: NUMBER={} TIMESTAMP={} AUTHOR={} MESSAGE="{}">'.format(self._num, self.date_time, self.author, self.text)

    def __str__(self):
        out = '"' + str(self._num) + '","' + self.author + '","' + str(self.date_time) + '","' + self.text + '"\n'
        return out

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

    def _date_parse(self, date):
        if type(date) is datetime.datetime:
            return date
        else:
            return datetime.datetime(*date)

    def sent_by(self, name):
        return self.author == name

    def sent_before(self,date):
        date = self._date_parse(date)
        return self.date_time < date

    def sent_after(self,date):
        date = self._date_parse(date)
        return self.date_time > date

    def sent_between(self, beg, end):
        beg = self._date_parse(beg)
        end = self._date_parse(end)
        return beg < self.date_time < end
