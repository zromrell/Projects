
import random
import logging

from messages import Upload, Request
from util import evenSplit
from peer import Peer

class FairTorrent(Peer):
    def postInit(self):
        self.optUnchoked = None    
        self.deficit = {} # collection of peerId : uploads-downloads
        print("postInit(): %s here!" % self.id)
        
        
    def requests(self, peers, history):
        round = history.currentRound()
        #utilizes same rarest first strategy as BitTorrent and BitTyrant
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
            allPieces = {}
            for peer in peers:
                availablePieceSet = set(peer.availablePieces)
                requestSet = availablePieceSet.intersection(npSet)
                requestList = list(requestSet)
                for piece in requestList:
                    if piece in allPieces:
                        allPieces[piece].append(peer.id)
                    else:
                        allPieces[piece] = [peer.id]
            allSortedPieces = dict(sorted(allPieces.items(), key=lambda item: len(item[1])))
            peerReqNum = {}
            for piece in allSortedPieces.items():
                #iterates through peers who have given piece
                for peer in piece[1]:
                    if peer in peerReqNum:
                        if peerReqNum[peer] <  self.maxRequests:
                            startBlock = self.pieces[piece[0]]
                            r = Request(self.id, peer, piece[0], startBlock)
                            requests.append(r)
                            peerReqNum[peer] += 1
                    else:
                        peerReqNum[peer] = 1
                        startBlock = self.pieces[piece[0]]
                        r = Request(self.id, peer, piece[0], startBlock)
                        requests.append(r)

        return requests
    
    def uploads(self, requests, peers, history):
        
        #gets current round
        round = history.currentRound()
        
        #access download and upload history of self
        selfHist = history
        uploads = []
        
        #initialize uploads for first round
        if round == 0:
            for peer in peers:
                self.deficit[peer.id] = 0
            
            
            peerDownloads = selfHist.downloads
            peerUploads = selfHist.uploads
            #update deficit by subtracting number of blocks you've received from peer i
            for down in peerDownloads:
                if down.fromId in self.deficit:
                    deficit[down.fromId] -= down.blocks
                else:
                    deficit[down.fromId] = down.blocks * -1
                #update deficit by adding bandwidth you've uploaded to peer i 
                    for up in peerUploads:
                        if up.toId in self.deficit:
                            deficit[up.toId] += up.bw
                        else:
                            deficit[up.toId] = up.bw
                            
        #if round > 0
        else:
        
            lastRoundDown = selfHist.downloads[-1]
            lastRoundUp = selfHist.uploads[-1]
        
            #updates deficit for latest round
            for down in lastRoundDown:
                if down.fromId in self.deficit:
                    self.deficit[down.fromId] -= down.blocks
                else:
                    self.deficit[down.fromId] = down.blocks * -1
            
            for up in lastRoundUp:
                if up.toId in self.deficit:
                    self.deficit[up.toId] += up.bw
                else:
                    self.deficit[up.toId] = up.bw
        #sort deficit by lowest to highest deficit
        sortedDeficit = dict(sorted(self.deficit.items(), key=lambda item: item[1]))
        self.deficit = sortedDeficit
        deleteSeeds = []
        #removes seeds from deficit 
        for key in self.deficit:
            if "Seed" in key:
                deleteSeeds.append(key)
        for seed in deleteSeeds:
            self.deficit.pop(seed,None)
        #if FairTorrent has no requests
        if len(requests) == 0:
            logging.debug("No one wants my pieces!")
            return []
        #FairTorrent has requests
        else: 
            #checks requests in increasing order of deficits
            uploadInfo = []
            for key in self.deficit.items():
                for req in requests:
                    if key[0] == req.requesterId:
                        uploadInfo.append(req.requesterId)
            #uploads until run out of bandwidth 
            bws = evenSplit(self.upBw, len(uploadInfo))
            count = 0
            for requestId in uploadInfo:
                tempUpload = Upload(self.id, requestId, bws[count])
                uploads.append(tempUpload)
                count += 1
            #upload to 4 peers; replace with above lines if you want to change S active slots
            '''
            bws = evenSplit(self.upBw, 3)
            if len(uploadInfo) >= 3: 
                for i in range(3):
                    tempUpload = Upload(self.id, uploadInfo[i], bws[i])
                    uploads.append(tempUpload)
            else:
                count = 0
                for reqId in uploadInfo:
                    tempUpload = Upload(self.id, reqId, bws[count])
                    uploads.append(tempUpload)
                    count +=1
            '''

        return uploads
                    
            
            
                
                
            

        
        
            
            
