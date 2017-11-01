from slackclient import SlackClient
import time
import os
import sys
import datetime

servers = ("fd2a", "ff1a", "hh3b", "kw1a", "kw1b", "lo8a", "os5a", "os5b", "sg2a", "sg2b", 'sy1a', 'va1a', 'va1b')
types = ("", "nfs", "cluster")

currser = "d"
currtype = ""
used = {}
total = {}
available = {}
ts = 0

dir_name = "data"


def savedata(dir_path, filename, data):
    f = open(dir_path + filename, "w")  # opens file with name of "test.txt"
    print(dir_path + filename)
    f.write(data)
    f.close()


def reset_data():
    print("datareset")
    for i in range(0, len(servers)):
        for j in range(0, len(types)):
            used[servers[i] + types[j]] = 0
            total[servers[i] + types[j]] = 0
            available[servers[i] + types[j]] = 0


def write_data(ts):
    datastr = ''
    global used
    global total
    ttotaltotalsum = 0

    for j in range(0, len(types)):

        datastr += types[j] + '\n'
        datastr += "Name\t" + "Region\t" + "total(TB)\t" + "used(TB)\t" + "available(TB)\t"+ "Used(%)\n"
        for i in range(0, len(servers)):
            tused = used[servers[i] + types[j]]
            ttotal = total[servers[i] + types[j]]
            ttotaltotalsum += ttotal
            if (ttotal != 0):
                datastr += (
                    servers[i][0:len(servers[i]) - 1] + "\t\t" +
                    servers[i][len(servers[i]) - 1] + "\t\t" +

                    "{:.1f}".format(ttotal / 1024) + " \t\t" +
                    "{:.1f}".format(tused / 1024) + " \t\t" +
                    "{:.1f}".format((ttotal - tused) / 1024) +
                    "{:.1f}".format(tused / ttotal*100) + " \t\t" +

                    "  \n")

    print("..")
    if (ttotaltotalsum > 0):
        if datetime.datetime.now().hour < 12:
            savedata("data/", "Storage-Update-M-" +
                     str(datetime.datetime.now().day) + "-" +
                     str(datetime.datetime.now().month) + "-" +
                     str(datetime.datetime.now().year) + ".txt", datastr)
        else:
            savedata("data/", "Storage-Update-E-" +
                     str(datetime.datetime.now().day) + "-" +
                     str(datetime.datetime.now().month) + "-" +
                     str(datetime.datetime.now().year) + ".txt", datastr)


def parse(text):
    global currser
    global currtype
    global used
    global total
    global available
    global ts

    content = text.split("\n")

    for line in content:
        line = line[:len(line)]

        if line.__contains__("Netapp Cluster"):
            for server in servers:

                if line.__contains__(server):
                    currser = server
                    for type in types:
                        if line.__contains__(type):
                            currtype = type


                            # print(line)

        if line.__contains__("Total available capacity"):
            # print(line)

            # print ("contains","Total available capacity------")

            elements = line.split(":")
            # print (elements)
            size = float(elements[1])
            # print(size)
            total[currser + currtype] += size
            # print(size,"TOTAL capacity",total)

        elif line.__contains__("size provisioned"):
            # print(line)

            # print("contains", "Total   LUN    size  provisioned------- ")
            elements = line.split(":")
            # print(elements)
            size = float(elements[1])
            # print(size)
            used[currser + currtype] += size
            # print(size, "Used", used)

    # print( currser)
    # print( currtype)
    # print(    used)
    # print(total)
    # print(available)
    return (used, total)


def make_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def main():
    slack_token = "your organization Token"
    channel_name = 'Your organization channel name'
    time_on_last_message = time.time()
    channel_id = ""
    ts = 0.000
    threshmins = 20
    channels_call = SlackClient(slack_token).api_call("channels.list")
    print(channels_call)
    for channel in channels_call["channels"]:
        if channel["name"] == channel_name:
            channel_id = channel["id"]
            print(channel)

    make_dir(dir_name)
    print(channel_id)
    reset_data()
    time_since_last_update = time.time() - time_on_last_message
    print("Waiting for new data....", time.time() - time_on_last_message)
    if time_since_last_update > threshmins * 60:
        write_data(ts)

        reset_data()

    sc = SlackClient(slack_token)

    data = sc.api_call(
        "channels.history",
        channel=channel_id,
        count=500,
    )

    if (data['ok'] == True):
        messages = data['messages']

        for message in reversed(messages):
            # print(message['ts'])
            if float(message['ts']) > ts:
                print("difference=", float(message['ts']) - ts)
                if float(message['ts']) - ts > (threshmins * 60):
                    print("greater diffrrece>reset................")
                    write_data(ts)

                    reset_data()

                time_on_last_message = time.time()

                ts = float(message['ts'])

                parse(message['text'])

    else:
        print("No data returned or error")

    time.sleep(5)  # in Seconds


main()
