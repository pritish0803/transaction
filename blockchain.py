import hashlib,json,sys

def hashMe(msg=""):
    if type(msg)!=str:
        msg=json.dumps(msg,sort_keys=True)
    if sys.version_info.major==2:
        return unicode(hashlib.sha256(msg).hexdigest(),'utf-8')
    else:
        return hashlib.sha256(msg).hexdigest()
import random
random.seed(0)

def makeTransaction(maxValue=8):

    sign=int(random.getrandbits(1))*2 - 1
    amount=random.randint(1,maxValue)
    alicePays = sign * amount
    bobPays   = -1 * alicePays
    return {u'Alice':alicePays,u'Bob':bobPays}

txnBuffer = [makeTransaction() for i in range(30)]

def updateState(txn,state):
    state=state.copy()
    for key in txn:
        if key in state.keys():
            state[key]+=txn[key]
        else:
            state[key]-=txn[key]
    return state
def isValidTransaction(txn,state):
    if sum(txn.values()) is not 0:
        return False
    for key in txn.keys():
           if key in state.keys():
               acctBalance = state[key]

           else:
                acctBalance = 0
                if (acctBalance + txn[key]) < 0:
                    return False

    return True
state = {u'Alice':50, u'Bob':50}
genesisBlockTxns = [state]
genesisBlockContents = {u'blockNumber':0,u'parentHash':None,u'txnCount':1,u'txns':genesisBlockTxns}
genesisHash = hashMe( genesisBlockContents )
genesisBlock = {u'hash':genesisHash,u'contents':genesisBlockContents}
genesisBlockStr = json.dumps(genesisBlock, sort_keys=True)

chain = [genesisBlock]


def makeBlock(txns,chain):
    parentBlock=chain[-1]
    parentHash=parentBlock[u'hash']
    blockNumber=parentBlock[u'contents'][u'blockNumber']+1

    txnCount=len(txns)
    blockContents = {u'blockNumber':blockNumber,u'parentHash':parentHash,u'txnCount':txnCount,u'txns':txns}
    blockHash=hashMe(blockContents)
    block={u'hash':blockHash,u'contents':blockContents}

    return block


blockSizeLimit=5

while len(txnBuffer)>0:
    bufferStartSize=len(txnBuffer)

    txnList=[]
    while len(txnBuffer)>0 and len(txnList)<blockSizeLimit:
        newTxn=txnBuffer.pop()
        validTxn=isValidTransaction(newTxn,state)
        if isValidTransaction:
            txnList.append(newTxn)
            state=updateState(newTxn,state)
            print state
        else:
            print "ignore Transaction"
            sys.stdout.flush()
            continue
    myBlock=makeBlock(txnList,chain)
    chain.append(myBlock)

def checkBlockHash(block):

    expectedHash=hashMe(block['contents'])
    if block['hash']!=expectedHash:
        raise Exception('Hash does not match contents of block %s'%block['contents']['blockNumber'])
    return


def checkBlockValidity(block,parent,state):

    parentNumber = parent['contents']['blockNumber']
    parentHash   = parent['hash']
    blockNumber  = block['contents']['blockNumber']

    for txn in block['contents']['txns']:
        if isValidTransaction(txn,state):
            state = updateState(txn,state)
        else:
            raise Exception('Invalid transaction in block %s: %s'%(blockNumber,txn))

    checkBlockHash(block)

    if blockNumber!=(parentNumber+1):
        raise Exception('Hash does not match contents of block %s'%blockNumber)

    if block['contents']['parentHash'] != parentHash:
        raise Exception('Parent hash not accurate at block %s'%blockNumber)
    return state


def checkChain(chain):

    if type(chain)==str:
        try:
            chain = json.loads(chain)
            assert( type(chain)==list)
        except:
            return False
    elif type(chain)!=list:
        return False

    global state


    for txn in chain[0]['contents']['txns']:
        state = updateState(txn,state)
        checkBlockHash(chain[0])
        parent = chain[0]



    for block in chain[1:]:
        state = checkBlockValidity(block,parent,state)
        parent = block
        

    return state

print checkChain(chain)

for i in chain:
    print i,"\n"
