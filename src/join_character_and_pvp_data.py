import sys
import pandas as pd
import numpy as np

if __name__ == "__main__":

    characterData = pd.read_csv(sys.argv[1])
    characterData.loc[:, 'id'] = characterData.loc[:, 'id'].astype(np.int64)
    characterData.loc[:, 'realm'] = characterData.loc[:, 'realm'].str.lower()
    characterData = characterData.set_index(['realm', 'name', 'id'])
    
    pvpData = pd.read_csv(sys.argv[2])
    pvpData.loc[:, 'id'] = pvpData.loc[:, 'id'].astype(np.int64)
    pvpData.loc[:, 'realm'] = pvpData.loc[:, 'realm'].str.lower()
    pvpData = pvpData.set_index(['realm', 'name', 'id'])

    joinedData = characterData.join(pvpData, rsuffix='_pvp')

    unnamed = [k for k in joinedData.columns if 'Unnamed' in k]

    joinedData.drop(unnamed, axis=1).to_csv(sys.argv[3])
