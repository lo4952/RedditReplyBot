#!/usr/bin/python
import praw
import pdb
import re
import os
import pprint

# splits set into character names and series names
def split_by_type(wiki_set, wiki_words, lower_wiki_words, char_list, series_list):
    all_locations = []
    for x in wiki_set:
        if x in lower_wiki_words:
            pos = lower_wiki_words.index(x)
            if wiki_words[pos + 1].startswith('http'):
                # add entry to list of series
                series_list.append(wiki_words[pos]) 
            elif wiki_words[pos + 2].startswith('http'):
                # add entry and link to list
                char_list.append(wiki_words[pos])
                char_list.append(wiki_words[pos + 2])


def make_char_text(char_list):
    temp_str = ""
    for i in range(0, len(char_list), 2):
        if i is 0:
            temp_str = "[" + char_list[i] + "]" + "(" + char_list[i + 1] + ")"
        else:
            temp_str = temp_str + ", " + "[" + char_list[i] + "]" + "(" + char_list[i + 1] + ")"
    # [Name](Link), [Name2](Link), ...
    return temp_str

def find_series_char(series_list, wiki_words):
    series_char_list = []
    temp_str = ""
    for x in series_list:
        # for each series, find all occurances
        series_locations = [i for i, y in enumerate(wiki_words) if y == x]
        for i in series_locations:
            # add entry and link to list
            series_char_list.append(wiki_words[i - 1])
            series_char_list.append(wiki_words[i + 1])
        if i is 0:
            temp_str = ("Characters from " + x + ": " 
            + make_char_text(series_char_list) + "\n")
        else:
            temp_str = (temp_str + "Characters from " + x + ": " 
            + make_char_text(series_char_list) + "\n")
        #print(temp_str)
    return temp_str

reddit = praw.Reddit('bot1')
subreddit = reddit.subreddit("lo4952_replybot")

# get the wiki page to use in searches
wikipage = reddit.subreddit('iateacrayon').wiki['list']

# if the file to track replies doesn't exist, create it
if not os.path.isfile("posts_replied_to.txt"):
    posts_replied_to = []
else :
    with open("posts_replied_to.txt", "r") as f:
        posts_replied_to = f.read()
        posts_replied_to = posts_replied_to.split("\n") # list post id's on seperate lines
        posts_replied_to = list(filter(None, posts_replied_to)) # eliminate empty values

# if the file to track comments doesn't exist, create it
if not os.path.isfile("comments_replied_to.txt"):
    comments_replied_to = []
else :
    with open("comments_replied_to.txt", "r") as f:
        comments_replied_to = f.read()
        comments_replied_to = comments_replied_to.split("\n") # list post id's on seperate lines
        comments_replied_to = list(filter(None, comments_replied_to)) # eliminate empty values
    
# check last 5 posts in hot for keywords in the title
for submission in subreddit.new(limit=5):
    if submission.id not in posts_replied_to:
        # regex to isolate phrases from wiki and title
        wiki_words = re.split(r'[\t\n\r\|]+', wikipage.content_md)
        # isolate words in square brackets
        m = re.search(r"\[([A-Za-z0-9_]+)\]", submission.title)
        title_mod = m.group(1)
        title_words = title_mod.split(", ")
        #title_words = [i.split(',')[0] for i in title_mod] 
        #set to lowercase to allow case-insensitive matching
        lower_wiki_words = [item.lower() for item in wiki_words]
        title_words = [item.lower() for item in title_words]
        # check if name is in wiki
        wiki_set = set(title_words).intersection(lower_wiki_words)
        print(title_mod) # debug use only

        if not wiki_set:
            print("No character names found in title: ", submission.title)
        else:
            char_list = []
            series_list = []
            full_comment = ""

            # sort and fill lists
            split_by_type(wiki_set, wiki_words, lower_wiki_words, char_list, series_list)
            if char_list:
                full_comment = "Characters: " + make_char_text(char_list) + "\n"
            
            # recognizes single-word series in title, may add later
            #if series_list:
                # find characters and create links
                #full_comment = full_comment + find_series_char(series_list, wiki_words)
            
            # print(full_comment)
            # submission.reply(full_comment)
            # posts_replied_to.append(submission.id)
        
        with open("posts_replied_to.txt", "w") as f:
            for post_id in posts_replied_to:
                f.write(post_id + "\n")

# Reply to comments with a specific keyword 
for sub in subreddit.new(limit=100):
    for c in sub.comments:
        if c.id not in comments_replied_to:
            wiki_words = re.split(r'[\t\n\r\|]+', wikipage.content_md)
            lower_wiki_words = [item.lower() for item in wiki_words]

            # required format: BOT CALL NAME1, NAME2, NAME3, ...
            char_list = []
            series_list = []
            full_comment = ""
            text = c.body.split()
            text = [item.lower() for item in text]
            text[0:1] = [''.join(text[0:1])]
            #for x in text:
                #print(x)
            if text[0] is "bot call":
                text_set = set(text).intersection(lower_wiki_words)
                split_by_type(text_set, wiki_words, lower_wiki_words, char_list, series_list)
                if char_list:
                    full_comment = "Characters: " + make_char_text(char_list) + "\n"
                if series_list:
                    full_comment = full_comment + find_series_char(series_list, wiki_words)
                print(full_comment)
                #c.reply(full_comment)
                #comments_replied_to.append(c.id)

            with open("comments_replied_to.txt", "w") as f:
                for c_id in comments_replied_to:
                    f.write(c_id + "\n")
