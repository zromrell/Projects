## BitTorrent Simulator 

* This simulator code has been adapted from David Parkes and Sven Seuken.
* See PDF for more details.  
* You do not have permission to share this code outside CS357.

This document details the general format of the BitTorrent simulator along with the detailed tests we ran to analyze client performance. 

This is the general format for the simulator:
python3 sim.py --loglevel=info --numPieces=16 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Client1,X Client2,Y ... Client3,Z 

--loglevel: info, debug

--numPieces: int

--blocksPerPiece: int 

--minBw: int < maxBw

--maxBw: int > minBw

--maxRound: int

--iters: int

X,Y,Z: int

The remaining section of this file details the extensive number of  simulation prompt commands: Some of these tests require changes to specific files such as bittorent.py and bittyrant.py. *BT denotes that specific variables need to be changed in the BitTyrant file. 

Free rider vs. BitTorrent … 1V9, 5v5, 9v1… different piece sizes up fixed block size

9v1
python3 sim.py --loglevel=info --numPieces=16 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,1 Freerider,9

python3 sim.py --loglevel=info --numPieces=32 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,1 Freerider,9

python3 sim.py --loglevel=info --numPieces=64 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,1 Freerider,9

python3 sim.py --loglevel=info --numPieces=128 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,1 Freerider,9

python3 sim.py --loglevel=info --numPieces=256 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,1 Freerider,9


5v5
python3 sim.py --loglevel=info --numPieces=16 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,5 Freerider,5

python3 sim.py --loglevel=info --numPieces=32 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,5 Freerider,5

python3 sim.py --loglevel=info --numPieces=64 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,5 Freerider,5

python3 sim.py --loglevel=info --numPieces=128 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,5 Freerider,5

python3 sim.py --loglevel=info --numPieces=256 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,5 Freerider,5

1v9
python3 sim.py --loglevel=info --numPieces=16 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,9 Freerider,1

python3 sim.py --loglevel=info --numPieces=32 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,9 Freerider,1

python3 sim.py --loglevel=info --numPieces=64 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,9 Freerider,1

python3 sim.py --loglevel=info --numPieces=128 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,9 Freerider,1


python3 sim.py --loglevel=info --numPieces=256 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,9 Freerider,1

BitTyrant vs BitTorrent
1v9 (with requests new rare, initialization u_p = 1, r = 3, gamma = .1, delta = .2) *BT
1v9 (with requests new rare, initialization u_p = 5, r = 3, gamma = .1, delta = .2) *BT
1v9 (with requests new rare, initialization u_p = 10, r = 3, gamma = .1, delta = .2) *BT
python3 sim.py --loglevel=info --numPieces=16 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,1 BitTorrent,9

python3 sim.py --loglevel=info --numPieces=32 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,1 BitTorrent,9

python3 sim.py --loglevel=info --numPieces=64 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,1 BitTorrent,9

python3 sim.py --loglevel=info --numPieces=128 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,1 BitTorrent,9

python3 sim.py --loglevel=info --numPieces=256 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,1 BitTorrent,9


5v5 (with requests new rare, initialization u_p = 1, r = 3, gamma = .1, delta = .2) *BT
5v5 (with requests new rare, initialization u_p = 5, r = 3, gamma = .1, delta = .2) *BT
5v5 (with requests new rare, initialization u_p = 10, r = 3, gamma = .1, delta = .2) *BT

python3 sim.py --loglevel=info --numPieces=16 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,5 BitTorrent,5

python3 sim.py --loglevel=info --numPieces=32 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,5 BitTorrent,5

python3 sim.py --loglevel=info --numPieces=64 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,5 BitTorrent,5

python3 sim.py --loglevel=info --numPieces=128 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,5 BitTorrent,5

python3 sim.py --loglevel=info --numPieces=256 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,5 BitTorrent,5

9v1 (with requests new rare, initialization u_p = 1, r = 3, gamma = .1, delta = .2) *BT
9v1 (with requests new rare, initialization u_p = 5, r = 3, gamma = .1, delta = .2) *BT
9v1 (with requests new rare, initialization u_p = 10, r = 3, gamma = .1, delta = .2) *BT
python3 sim.py --loglevel=info --numPieces=16 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,9 BitTorrent,1

python3 sim.py --loglevel=info --numPieces=32 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,9 BitTorrent,1

python3 sim.py --loglevel=info --numPieces=64 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,9 BitTorrent,1

python3 sim.py --loglevel=info --numPieces=128 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,9 BitTorrent,1


python3 sim.py --loglevel=info --numPieces=256 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTyrant,9 BitTorrent,1


BitTorrent vs. FairTorrent … 1V9, 5v5, 9v1… different piece sizes up fixed block size

9v1
python3 sim.py --loglevel=info --numPieces=16 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,1 FairTorrent,9

python3 sim.py --loglevel=info --numPieces=32 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,1 FairTorrent,9

python3 sim.py --loglevel=info --numPieces=64 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,1 FairTorrent,9

python3 sim.py --loglevel=info --numPieces=128 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,1 FairTorrent,9

python3 sim.py --loglevel=info --numPieces=256 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,1 FairTorrent,9


5v5
python3 sim.py --loglevel=info --numPieces=16 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,5 FairTorrent,5

python3 sim.py --loglevel=info --numPieces=32 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,5 FairTorrent,5

python3 sim.py --loglevel=info --numPieces=64 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,5 FairTorrent,5

python3 sim.py --loglevel=info --numPieces=128 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,5 FairTorrent,5

python3 sim.py --loglevel=info --numPieces=256 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,5 FairTorrent,5

1v9
python3 sim.py --loglevel=info --numPieces=16 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,9 FairTorrent,1

python3 sim.py --loglevel=info --numPieces=32 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,9 FairTorrent,1

python3 sim.py --loglevel=info --numPieces=64 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,9 FairTorrent,1

python3 sim.py --loglevel=info --numPieces=128 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,9 FairTorrent,1


python3 sim.py --loglevel=info --numPieces=256 --blocksPerPiece=16 --minBw=16 --maxBw=64 --maxRound=1000 --iters=40 Seed,2 BitTorrent,9 FairTorrent,1
