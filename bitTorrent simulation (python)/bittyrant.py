import random
import logging
from messages import Upload, Request
from util import evenSplit
from peer import Peer

class BitTyrant(Peer):
    def postInit(self):  
        print("postInit(): %s here!" % self.id)
        self.expDownload = {}
        self.expUpload4Rec = {}
        self.easyPeer = {}
        self.gamma = 0.1
        self.delta = 0.1
        
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
                        #allPieces[placeHolder.index(piece)][1].append(peer.id)
                    else:
                        #first time seeing piece so add to allPieces
                        allPieces[piece] = [peer.id]    
                    
            #sorts pieces by rarity (least number of owners)
            keys = list(allPieces.keys())
            random.shuffle(keys)
            allRandomPieces = {}
            for key in keys:
                #newList = allPieces[key]
                #random.shuffle(newList)
                #allRandomPieces[key] = newList
                allRandomPieces[key] = allPieces[key]

            allSortedPieces = dict(sorted(allRandomPieces.items(), key=lambda item: len(item[1])))
            
            
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

        round = history.currentRound()
        logging.debug("%s again.  It's round %d." % (
            self.id, round))
        # One could look at other stuff in the history too here.
        # For example, history.downloads[round-1] (if round != 0, of course)
        # has a list of Download objects for each Download to this peer in
        # the previous round.

        #initialized or updates U_p
        if round == 0: #intialization
            for peer in peers:
                if "Seed" not in peer.id:
                    theUpBw = random.randint(self.conf.minUpBw, self.conf.maxUpBw)
                    self.easyPeer[peer.id] = peer
                    #self.expDownload[peer.id] = 2
                    self.expDownload[peer.id] = theUpBw / 4
                    self.expUpload4Rec[peer.id] = 1
            
        elif round <= 2:
            if round == 1:
                exit
            else:
                downloadHist = history.downloads[round-1]
                for download in downloadHist:
                    if "Seed" not in download.fromId:
                        self.expDownload[download.fromId] = download.blocks
                    
        elif round > 2: #two cases to update self.expUpload4Rec
            uploadHist = history.uploads[-2]
            #downloadHist = history.downloads[-3:]
            downloadHist = history.downloads[-3:]

            #update d_p based on previous rounds downloads
            for download in downloadHist[-1]:
                if "Seed" not in download.fromId:
                    self.expDownload[download.fromId] = download.blocks

            #uses history to update u_p for indiviudals who have unchoked for the last r rounds
            downloadPeers = set()
            downloadPeersRound = set()
            for downloadRound in downloadHist:
                count = 0
                for download in downloadRound:
                    if "Seed" not in download.fromId:
                        if count == 0:
                            downloadPeers.add(download.fromId)
                        else:
                            downloadPeersRound.add(download.fromId)
                downloadPeers = downloadPeers.intersection(downloadPeersRound)
                
            for peerId in list(downloadPeers):
                self.expUpload4Rec[peerId] *= (1 - self.gamma)

            #uses history to update u_p for individuals who didn't reciprocate
            uploadedToPeers = set()
            downloadPeers = set()
            noRecip = set()
            for upload in uploadHist:
                uploadedToPeers.add(upload.toId)
            for download in downloadHist[-1]:
                if "Seed" not in download.fromId:
                    downloadPeers.add(download.fromId)
                
            noRecip = uploadedToPeers.difference(downloadPeers)
            for peerId in list(noRecip):
                self.expUpload4Rec[peerId] *= (1 + self.delta)   
                
        if len(requests) == 0:
            logging.debug("No one wants my pieces!")
            uploads = []
        else:
            logging.debug("Still here: uploading to a random peer")
            uploads = []
            
            
            ratio = {key: self.expDownload[key]/self.expUpload4Rec[key] for key in self.expDownload}
            rank = dict(sorted(ratio.items(), key=lambda item: item[1], reverse = True))
            requestId = [x.requesterId for x in requests]
            
            upCount = 0
            for key in rank:
                if key in requestId:
                    if upCount + self.expUpload4Rec[key] < (self.upBw):
                        uploads.append(Upload(self.id, key, self.expUpload4Rec[key]))
                        upCount += self.expUpload4Rec[key]
            
        return uploads
