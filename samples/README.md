__`facebook_and_sms.py`__

The file contains code to merge a parsed Facebook Message history with an iOS6 iPhone Message history
(using the code from [iphone_message_parser](https://github.com/jsharkey13/iphone_message_parser)). The
resulting object can be used with the `fb_analysis.py` code, or browsed as if it was an `fb_chat.Chat` object.

-----

__`sample_date_graph.png`__

The image is the graph produced from a parsed Facebook Message history, using the code from `fb_parser.py`
to produce the `Facebook.Chat` object.
The code to produce the graph is in `fb_analysis.py` and requires a single command:
```
fb_analysis.messages_date_graph(Facebook.Chat, name="Their Name", filename="sample_date_graph.png",
                                start_date=(2014, 9, 1), end_date=(2015, 5, 1), no_gui=True)
```

-----

__`sample_pie_chart.png`__

The image is again a graph produced using `fb_analysis.py`:
```
fb_analysis.messages_pie_chart(Facebook.Chat, N=8, filename="sample_pie_chart.png", count_type="total", groups=False,
                               no_gui=True, percentages=False)
