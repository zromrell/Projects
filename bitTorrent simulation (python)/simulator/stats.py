# Code adapted from Sven Seuken, University of Zurichn

class Stats:
    @staticmethod
    def uploadedBlocks(peerIds, history):
        """
        peerIds: list of peerIds
        history: a History object

        Returns:
        dict: peerId -> total upload blocks used
        """
        uploaded = dict((peerId, 0) for peerId in peerIds)
        for peerId in peerIds:
            for ds in history.downloads[peerId]:
                for download in ds:
                    uploaded[download.fromId] += download.blocks
                
        return uploaded

    

    @staticmethod
    def uploadedBlocksStr(peerIds, history):
        """ Return a pretty stringified version of uploaded_blocks """
        d = Stats.uploadedBlocks(peerIds, history)

        #k = lambda id: d[id]
        return "\n".join("%s: %d, bw=%d" % (id, d[id], history.uploadRates[id])
                         for id in sorted(d, key=d.get))


        
    @staticmethod
    def completionRounds(peerIds, history):
        """Returns dict: peer_id -> round when completed,
        or -1 if not completed"""
        d = dict(history.roundDone)
        for id in peerIds:
            if id not in d:
                d[id] = -1 
        return d

    @staticmethod
    def completionRoundsStr(peerIds, history):
        """ Return a pretty stringified version of completionRounds """
        d = Stats.completionRounds(peerIds, history)
        return "\n".join("%s: %s" % (id, d[id])
                         for id in sorted(d, key=d.get))
        #return "Not completed \n:" + "\n".join("%s: %s" % 
        #       id for id in d)
    

    @staticmethod
    def allDoneRound(peerIds, history):
        d = Stats.completionRounds(peerIds, history)
        dVal = d.values()
        if -1 in dVal:
            return -1
        return max(dVal)
    
