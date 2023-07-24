import random
import logging

from messages import Upload, Request
from util import evenSplit
from peer import Peer

class BitExpose(Peer):
    def postInit(self):  
        print("postInit(): %s here!" % self.id)
        self.expDownload = {}
        self.expUpload4Rec = {}
        self.easyPeer = {}
        self.gamma = 0.1
        self.delta = 0.2
        
    def requests(self, peers, history):
        """
        peers: available info about the peers (who has what pieces) 
        history: what's happened so far as far as this peer can see

        returns: a list of Request() objects

        This will be called after updatePieces() with the most recent state.
        """
        '''
        needed = lambda i: self.pieces[i] < self.conf.blocksPerPiece
        neededPieces = filter(needed, range(len(self.pieces)))
        npSet = set(neededPieces)  # sets support fast intersection ops


        logging.debug("%s here: still need pieces %s" % (
            self.id, list(npSet)))

        logging.debug("%s still here. Here are some peers:" % self.id)
        for p in peers:
            logging.debug("id: %s, available pieces: %s" % (p.id, p.availablePieces))

        logging.debug("And look, I have my entire history available too:")
        logging.debug(str(history))

        requests = []   # We'll put all the pieces we want here 
        # Symmetry breaking 
        random.shuffle(list(neededPieces))
        
        # Sort peers by id.
        peers.sort(key=lambda p: p.id)
        # request all available pieces from all peers
        # can request up to self.maxRequests from each
        for peer in peers:
            avSet = set(peer.availablePieces)
            isect = avSet.intersection(npSet)
            n = min(self.maxRequests, len(isect))
            # More symmetry breaking -- ask for random pieces.
            # This would be the place to try fancier piece-requesting strategies
            # to avoid getting the same thing from multiple peers at a time.
            for pieceId in random.sample(isect, n):
                # aha! The peer has this piece! Request it.
                # which part of the piece do we need next?
                # (must get the next-needed blocks in order)
                startBlock = self.pieces[pieceId]
                r = Request(self.id, peer.id, pieceId, startBlock)
                requests.append(r)
        '''
        
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
                    #placeHolder = [x[0] for x in allPieces]
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
                allRandomPieces[key] = allPieces[key]

            allSortedPieces = dict(sorted(allRandomPieces.items(), key=lambda item: len(item[1])))
        
            #allPieces.sort(key = lambda x :len(x[1]))

            #keeps track of peer and the number of requests to them. [peer, number of requests]
            peerReqNum = {}

            #iterates through [piece, [peer.id's]] already sorted by piece rarity
            for piece in allSortedPieces.items():
                #iterates through peers who have given piece
                for peer in piece[1]:
                
                    #strips peerReqNum into list of peers already encountered
                    #peerHolder = [x[0] for x in peerReqNum]
                
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
        
        if len(requests) == 0:
            logging.debug("No one wants my pieces!")
            uploads = []
        else:
            logging.debug("Still here: uploading to a random peer")
            uploads = []
            
            requestId = [x.requesterId for x in requests]

            
            
            
        
            uploads.append(Upload(self.id, random.choice(requestId), self.upBw))
            


        
        
        #initialized or updates U_p
       
        return uploads
