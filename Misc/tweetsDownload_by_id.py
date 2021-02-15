# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 19:33:48 2020

@author: Aviv
"""

import tweepy
import xlwt 
from xlwt import Workbook 
  

# These are provided to you through the Twitter API after you create a account
access_token = "1243499665858932736-9vUlTdXeSUl6tmCtOqLGaoY4bko4TN"
access_token_secret = "7WRYI4dqg83mym6A3TjA2A4SvN7zD52YALcoFHL2IGKWx"
consumer_key = "eyowxRQhHOBVSbL3pRBr2MyLb"
consumer_secret = "q8pDyBRxdWXoKt2Q7WLeOdtCJOKQMBjQCsdEwg6lVW8O8gwbDM"

class Event:
   def __init__(self, eid, label, tweets_list):
       self.eid = eid
       self.label = label
       self.tweets_list=tweets_list



#This code is for downloading tweets by their id

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

# set access to user's access key and access secret
auth.set_access_token(access_token, access_token_secret)

# calling the api
api = tweepy.API(auth)

#reding file containing Tweet's IDs
events_list_str=[]
events_list=[]
with open("/content/drive/My Drive/Colab repo/Twitter Download/Twitter.txt") as file:
    for line in file:
        line = line.strip()
        events_list_str.append(line)
        
for e in events_list_str:
    tweets_list=e.split(" ")
    tweets_list[0]=tweets_list[0].replace("\t", " ")
    properties=tweets_list[0].split(" ")
    properties[0] = properties[0].replace('eid:', '')
    properties[1] = properties[1].replace('label:', '')
    tweets_list[0] = properties[2]
    events_list.append(Event(properties[0],properties[1],tweets_list))
    
tweets_file = Workbook()
tweets_sheet = tweets_file.add_sheet('Tweets') 
log_file = open("/content/drive/My Drive/Colab repo/Twitter Download/log_tweets_download_6.txt","a+")
i=0 
for event in events_list[800:]:
    j=0
    failed = 0
    succeed = 0
    tweets_sheet.write(i,j,event.eid)
    j=j+1
    tweets_sheet.write(i,j,event.label)
    j=j+1
    for tweet_id in event.tweets_list:
        text=""
        # fetching the status
        try:
            status = api.get_status(tweet_id, tweet_mode='extended')
            text = status.full_text
            succeed = succeed+1
            print("fetching succeed")
        except:
            failed = failed+1
            print("fetching failed")
            pass
        # fetching the text attribute
        if j>254:
            j=0
            i=i+1
            tweets_sheet.write(i,j,event.eid)
            j=j+1
            tweets_sheet.write(i,j,event.label)
            j=j+1
        tweets_sheet.write(i,j,text)
        print("tweet",j-1, "is done")
        j=j+1
    tweets_file.save('/content/drive/My Drive/Colab repo/Twitter Download/tweets file rev1-6.xls')
    log_file.write(f'event {event.eid}: {succeed} tweets succeed and {failed} tweets failed.\n')
    print("---------------------------------event",event.eid,"is finished----------------------------")
    i=i+1
log_file.close()
  

"""   
# the ID of the status
id = 1246367648331399168

# fetching the status
status = api.get_status(id, tweet_mode='extended')

# fetching the text attribute
text = status.full_text

print("The text of the status is : \n\n" + text)
"""

