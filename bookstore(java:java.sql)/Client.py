#!/usr/local/bin/python
import xmlrpc.client, sys
#specify server hostname as command line argument
name = "http://"+sys.argv[1]+":8854"
server = xmlrpc.client.ServerProxy(name)
open = True


print("Welcome to the bookstore")
print("Enter \"help\" for usage hints")
invalidReq = "Invalid Request ... Enter \"help\" for usage hints"

while open:
    request = input("> ")
    tokens = request.split(" ", 1)

    if tokens[0] == "lookup":
        if tokens[1].isdigit():
            answer = server.sample.lookup(int(tokens[1]))
            print(answer[0])
        else:
            print(invalidReq)
    elif tokens[0] == "search":
        answer = server.sample.search(tokens[1])
        for i in answer:
            print(i)
    elif tokens[0] == "buy":
        if tokens[1].isdigit():
            answer = server.sample.buy(int(tokens[1]))
            print(answer[0])
        else:
            print(invalidReq)
    elif tokens[0] == "help":
        print("lookup <item_number> | look up a book using their item number")
        print("search <topic> | search for a book under a specific topic")
        print("buy <item_number> | buy the book using their item hunber")
        print("leave | Want to leave the bookstore?")
    elif tokens[0] == "leave":
        print("You left the bookstore")
        open = False
    else:
        print(invalidReq)
