# Code adapted from Sven Seuken, University of Zurich

# This is a simple peer that just illustrates how the code works 
# starter code is the same as rand.py

import random
import logging

from messages import Upload, Request
from util import evenSplit
from peer import Peer

class BitTorrent(Peer):
    def postInit(self):
        self.optUnchoked = None
        print("postInit(): %s here!" % self.id)
    
    def requests(self, peers, history):
        """
        peers: available info about the peers (who has what pieces) 
        history: what's happened so far as far as this peer can see
        returns: a list of Request() objects

        This will be called after updatePieces() with the most recent state.
        """
        round = history.currentRound()
        #creates a set of all the pieces the following peer needs
        needed = lambda i: self.pieces[i] < self.conf.blocksPerPiece
        neededPieces = filter(needed, range(len(self.pieces)))
        npSet = set(neededPieces)
        
        requests = []

        logging.debug("%s here: still need pieces %s" % (
            self.id, list(npSet)))
        logging.debug("%s still here. Here are some peers:" % self.id)
        for p in peers:
            logging.debug("id: %s, available pieces: %s" % (p.id, p.availablePieces))

        logging.debug("And look, I have my entire history available too:")
        logging.debug(str(history))

        #for first five rounds, request random piece 
        if round < 5:
            random.shuffle(list(neededPieces))
            peers.sort(key=lambda p: p.id)
            for peer in peers:
                avSet = set(peer.availablePieces)
                isect = avSet.intersection(npSet)
                #print(isect)
                n = min(self.maxRequests, len(isect))
                for pieceId in random.sample(isect, n):
                    startBlock = self.pieces[pieceId]
                    r = Request(self.id, peer.id, pieceId, startBlock)
                    requests.append(r)
        
        else:  
        # array of arrays [pieceId, [peers.id who have the following piece]]

            allPieces = {}
        
            for peer in peers:

            #creates list of pieces you want to request from peer
                availablePieceSet = set(peer.availablePieces)
                requestSet = availablePieceSet.intersection(npSet)
                requestList = list(requestSet)

            #add wanted piece to allPieces and keep track of peer.id
                for piece in requestList:
                    #strips allPieces into list of purely the pieces we have already encountered
                    
                    #checks if we have already encountered the following piece
                    if piece in allPieces:
                        #appends corresponding peer id to list of peer id's who have piece
                        allPieces[piece].append(peer.id)
                        
                    else:
                        #first time seeing piece so add to allPieces
                        allPieces[piece] = [peer.id]    
                    
            #sorts pieces by rarity (least number of owners)
            
            #random shuffling of pieces
            keys = list(allPieces.keys())
            random.shuffle(keys)
            allRandomPieces = {}
            for key in keys:
                #newList = allPieces[key]
                #random.shuffle(newList)
                #allRandomPieces[key] = newList
                allRandomPieces[key] = allPieces[key]
            
            
            allSortedPieces = dict(sorted(allRandomPieces.items(), key=lambda item: len(item[1])))
            
            #different sorting mechanism utilized in randomization tests 
            #comment out the below line for piece randomization
            #allSortedPieces = dict(sorted(allPieces.items(), key=lambda item: len(item[1])))
        
            #allPieces.sort(key = lambda x :len(x[1]))

            #keeps track of peer and the number of requests to them. [peer, number of requests]
            peerReqNum = {}

            #iterates through [piece, [peer.id's]] already sorted by piece rarity
            for piece in allSortedPieces.items():
                #iterates through peers who have given piece
                for peer in piece[1]:
                
                    #strips peerReqNum into list of peers already encountered
                    
                
                    #if already encountered
                    if peer in peerReqNum:
                        #if the number of requests corresponding to that peer hasn't exceded the maxRequests
                        if peerReqNum[peer] <  self.maxRequests:
                        #if peerReqNum[peerHolder.index(peer)][1] < self.maxRequests:
                            #create a request to that peer for that piece starting at a given block
                            startBlock = self.pieces[piece[0]]
                            r = Request(self.id, peer, piece[0], startBlock)
                            #append request
                            requests.append(r)
                            #update the number of requests for the specific peer
                            peerReqNum[peer] += 1
                    else:
                        #haven't encountered peer so add them setting their request number to 1
                        peerReqNum[peer] = 1
                    
                        startBlock = self.pieces[piece[0]]
                        r = Request(self.id, peer, piece[0], startBlock)
                        requests.append(r)
        
        return requests

    def uploads(self, requests, peers, history):
        """
        requests -- a list of the requests for this peer for this round
        peers -- available info about all the peers
        history -- history for all previous rounds

        returns: list of Upload objects.

        In each round, this will be called after requests().
        """
        
        #corresponding round number
        round = history.currentRound()
        
        #debug output
        logging.debug("%s again.  It's round %d." % (
            self.id, round))

        #if you receive no requests you do not need to upload to anyone (including optUnchoked, however, you still store that info)
        if len(requests) == 0:
            logging.debug("No one wants my pieces!")
            chosen = []
            bws = []
        else: #i.e. if you are receiving requests
            #debug ouput
            logging.debug("Still here: uploading to a random peer")
            
            #list of downloads from all rounds
            downloadHist = history.downloads
            if round > 1: #potentially last round versus last 2...
                #trims download history to last two rounds
                downloadHist = downloadHist[(round-2):]

            #keeps track of blocks downloaded from each peer downloaded from in history. [peer.id, download count]
            downloadCount = {}
            
            for downloadRound in downloadHist:
                for download in downloadRound:
                    #strips downloadCount to make list of peer's ids who you've downloaded from
                    
                    
                    #if you have already downloaded from this peer
                    if download.fromId in downloadCount:
                    #if download.fromId in downHolder:
                        #update the download count for them
                        downloadCount[download.fromId] += download.blocks
                    else:
                        #add the peer's id and the number of blocks they uploaded to you
                        downloadCount[download.fromId] = download.blocks
                        #downloadCount.append([download.fromId, download.blocks])

            #organizes [peer.id, download count] based on who uploaded to you the most
            sortedDownloadCount = dict(sorted(downloadCount.items(), key=lambda item: item[1], reverse = True))
            

            #strips downloadCount and makes list of peers in order of unchoke preference
            
            
            #creates list of all the individuals requesting to you
            mixed = []
            for peer in requests:
                if peer.requesterId in sortedDownloadCount:
                    mixed.append(peer.requesterId)
               
                
            requestId = [x.requesterId for x in requests]

            #creates list of individuals who are requesting you in order of unchoke preference 
            

            #counts for while loops
            

            chosen = []


            #creates list of peers who requested but have not uploaded to you
            remainList = list(set(requestId).difference(mixed))
            
            #unchokes based on upload bandwidth... to confirm even split is an integer of atleast 1
            #if the number of peers downloaded from who request is less than the unchoke slots (self.upBw) minus 1
            if len(mixed) < 4:
                #unchoke all of them
                chosen += mixed
                    
                
                
                #while you have remaining unchoke slors and there are still peers who requested you
                if len(remainList) != 0:
                    #randomly pop a peer
                    if len(remainList)< (4 - len(mixed)):
                        chosen += remainList
                    else:
                        unchoke = random.sample(remainList, (4 - len(mixed)))
                        #unchoke them
                        chosen += unchoke
                    
                    
                    
            else:
                #unchoke based on preference
                chosen += mixed[3:]
                        
            #change peer who you are optimistically unchoking        
            if round % 3 == 2:
                remainList = list((set(requestId)).difference(set(chosen)))
            
                    
                #optimistically unchokes individual who hasn't been unchoked yet
            
                if len(remainList) != 0:
                    self.optUnchoked = random.sample(remainList,1)

            if self.optUnchoked != None:
                chosen.append(self.optUnchoked)


            
            
            

        if len(chosen) == 0:
            return []
            
        bws = evenSplit(self.upBw, len(chosen))
            

        # create actual uploads out of the list of peer ids and bandwidths
        uploads = [Upload(self.id, peerId, bw)
                   for (peerId, bw) in zip(chosen, bws)]

        return uploads
