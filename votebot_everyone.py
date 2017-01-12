# This Piston/Python-Bot will vote for everyone who post except those flagged by
# @cheetah or @steemcleaners. By Default the Upvote is set at 2%
# Created by: @furion, @contentjunkie, @anyx, @inertia, @fyrstikken
# Make sure you have the latest version of Python and Piston installed
# See Original Post for details and step by step process.
# For help come on http://steemspeak.com or http://steemit.chat
#
# This version is from @thebatchman

from steem.steem import Steem
from steem.steem import BroadcastingError
import threading
import time
import random
import csv

# Default percent upvote and favorite percent upvote
percent_upvote = 3;
fav_percent_upvote = 100;

# This is the range (in seconds) in which your bot will cast a vote
# Default numbers are a 9 to 14 minute range
vote_delay = random.randrange(540,840)

# 0 disables tipping, 1 enables tipping (for favorite authors only)
tipping = 0

# Tipping amount
tip_amount = 0.001

# my favorite blogs on steemit
top_writers = []

# add my favorites
my_favorites = ["thebatchman"]

# Skiplist functionality has not been added yet, this will be your personal blacklist
with open('skiplist.txt', mode='r') as infile:
    reader = csv.reader(infile)
    for rows in reader:
        v = rows[0]
        top_writers.append(v)

def list_load(listfile):

    with open(listfile, 'r') as readstuff:

        listvar = []
        reader = csv.reader(readstuff)

        for rows in reader:
            v= rows[0]
            listvar.append(v)

    return listvar

# Create a accounts.txt file in the same directory as this script with your account
# If you want multiple accounts, just enter them in the accounts.txt with one account per line
# Same goes for the post_wif.txt file or the active_wif.txt file.
account = list_load("accounts.txt")

# Checks if tipping is enabled and loads the correct key file
if not tipping:
    posting_key = list_load("post_wif.txt")
else:
    active_key = list_load["active_wif.txt"]

upvote_history = []

my_subscriptions = top_writers + my_favorites

def feed():

    # Starting The Bot
    print("Upvote Bot Started - Waiting for New Posts to Upvote!")

    steem = Steem(wif=posting_key[0])
    for comment in steem.stream_comments():

        if True:
            # Just making sure we vote for the post and not a comment.
            if comment.depth == 0:

                # check if we already upvoted this. Sometimes the feed will give duplicates.
                if comment.identifier in upvote_history:
                    continue

                print("New post by @%s %s" % (comment.author, url_builder(comment)))
                workerThread = threading.Thread(name=comment.identifier, target=worker, args=(comment,))
                workerThread.start()

def url_builder(comment):
    return "https://steemit.com/%s/%s" % (comment.category, comment.identifier)

def worker(worker_comment):

    time.sleep(vote_delay)

    try:

        for (k,v) in enumerate(account):

            worker_steem = Steem(wif=posting_key[k])
            upvote_comment = worker_steem.get_content(worker_comment.identifier)

            # Checking if post is flagged for plagarism & spam by these accounts
            names = ['steemcleaners', 'cheetah']

            for avote in upvote_comment['active_votes']:

                if (avote['voter'] in names and avote['percent'] < 0):

                    print("====> Upvote Skipped - Post Flagged by Cheetah or Steemcleaners")
                    return False

            # Check if author is in your favorites. Then vote with % appropriately
            if upvote_comment.author in my_favorites:

                upvote_comment.vote(fav_percent_upvote, v)
                print("====> Voted %i%% succesfully with %s!" % (fav_percent_upvote,v) )

                if tipping:

                    send_a_tip(upvote_comment.author)
                    print("====> Sent $0.001 STEEM to @%s" % upvote_comment.author)

            else:
                upvote_comment.vote(percent_upvote, v)
                print("====> Voted %i%% succesfully with %s!" % (percent_upvote,v) )

            upvote_history.append(upvote_comment.identifier)

    except BroadcastingError as e:

        print("Upvoting failed...")
        print("We have probably already upvoted this post before the author edited it.")
        print(str(e))

# Tipping function
def send_a_tip(author):
    steem = Steem(wif=active_key)
    steem.transfer(author, tip_amount, "STEEM", memo="Keep Blogging", account=account)

if __name__ == "__main__":

    while True:

        try:

            feed()

        except (KeyboardInterrupt, SystemExit):

            print("Quitting...")
            break

        except Exception as e:

            traceback.print_exc()
            print("### Exception Occurred: Restarting...")

# If you want to add more complexity to the Bot, feel free to do so and share it with
# The Steemit community on your own Blog.
