"""
Clare
2019/07/03
"""


# Set robot
from wxpy import *
import datetime
from threading import Timer
import re
import schedule
import time

bot=Bot()
bot.cache_path=True
bot.enable_puid('wxpy_puid.pkl')


# find target groups, create empty new list to collect @ msgs
# find specific groups and add them to a list company_groups
company_groups = bot.groups().search('Test')
to_do_lists = []


# company_groups.append(company_group), add each target group to target groups
# create a new list for each target group and add it to the msg group - to_do_lists.
for company_group in company_groups:
    to_do_lists.append([])


# a loop for each target group
# if the msg is unaddressed, status=0; else status =1
# for each group, do a loop for each single to_do_list
# if msg_status=1, remove it from to_do_list
def send_news():
    global to_do_lists
    # print(to_do_list)
    i = 0
    for company_group in company_groups:
        msg_index = 0
        for to_do_msg in to_do_lists[i]:
            if(to_do_msg['status'] == 1):
                to_do_lists[i].remove(to_do_msg)
        for to_do_msg in to_do_lists[i]:
            msg_index = msg_index + 1
            if(to_do_msg['status'] == 0):
                company_group.send('待办序号: {},  消息内容: {} '.format(msg_index, to_do_msg['txt']))
                to_do_lists[i][msg_index - 1]['num'] = to_do_lists[i][msg_index - 1]['num'] + 1
        i = i + 1
        time.sleep(2)


def send_delay_news():
    global to_do_lists
    # print(to_do_list)
    i = 0
    for company_group in company_groups:
        msg_index = 0
        for to_do_msg in to_do_lists[i]:
            if(to_do_msg['status'] == 1):
                to_do_lists[i].remove(to_do_msg)
        for to_do_msg in to_do_lists[i]:
            msg_index = msg_index + 1
            if(to_do_msg['status'] == 0 and to_do_msg['num'] > 1):
                company_group.send('延误！ 待办序号: {},  延误天数: {}, 消息内容: {} '.format(msg_index, to_do_msg['num']-1, to_do_msg['txt']))
#            if(to_do_msg['status'] == 0 and to_do_msg['num'] == 1):
#                company_group.send('待办序号: {},  消息内容: {} '.format(msg_index, to_do_msg['txt']))
        i = i + 1
        time.sleep(2)
    # t = Timer(10, send_news)
    # t.start()


# check each msg received
# if it is an @ msg and it does not @ the bot, make it a to_do_msg and add it to to_do_list
# if it is an @ msg and it @ the bot and it is in the format "ad #", the corresponding to_do_msg's status is changed to 1
@bot.register(company_groups, TEXT)
def process_message(msg):
    global to_do_lists
    list_index = company_groups.index(msg.chat)
    if('@' in msg.text and msg.sender != bot.self and not msg.is_at):
        to_do_msg = {'txt':msg.text, 'status':0, 'num':1}
        to_do_lists[list_index].append(to_do_msg)
    if(('Ad' in msg.text or 'ad' in msg.text) and msg.is_at):
        num_list = re.findall("\d+", msg.text)
        num = 0
        if(len(num_list) >= 1):
            num = int(num_list[0])
        if((num <= len(to_do_lists[list_index])) and (num >= 1)):
            to_do_lists[list_index][num - 1]['status'] = 1
                # to_do_list.remove(to_do_list[num - 1])


# schedule a time when the bot should do send_news() or send_delay_news()
def on_time_send_news():
    # when using the bot, uncomment the following two lines
    # schedule.every().day.at("09:30").do(send_news)
    # schedule.every().day.at("13:30").do(send_delay_news)

    # the following two lines are for testing
    schedule.every(1).minutes.do(send_news)
    schedule.every(1).minutes.do(send_delay_news)
    while True:
        schedule.run_pending()
        time.sleep(2)



if __name__ == "__main__":
    on_time_send_news()
