import sys
import pandas as pd
import numpy as np
import json

COLUMNS = [
    'id', 'name', 'gender', 'faction', 'race', 'character_class',
    'active_spec', 'realm', 'guild', 'last_login_timestamp',
    'average_item_level', 'equipped_item_level', 'active_title'
    ]


def get_subfield(X, subfield, columns):
    z = []

    def f(x, subfield):
        if x is np.nan:
            return np.nan
        return x[subfield]

    for col in columns:
        current = X.loc[:, col].apply(lambda x: f(x, subfield))

        z.append(current)
        
    return pd.DataFrame(z, columns=X.index, index=columns).T


def process_character_data(raw):
    processed = pd.DataFrame(index=raw.index,
                             columns=COLUMNS)

    noprocessCols = ['id', 'name', 'average_item_level', 'equipped_item_level',
                     'last_login_timestamp']
    
    processed.loc[:, noprocessCols] = raw.loc[:, noprocessCols]

    nameCols = ['realm', 'guild', 'gender', 'faction', 'race',
                'character_class', 'active_spec', 'active_title']

    processed.loc[:, nameCols] = get_subfield(raw, 'name', nameCols)

    return processed.dropna(subset=['id'], axis=0)


if __name__ == "__main__":

    inFile = sys.argv[1]
    outFile = sys.argv[2]

    rawString = pd.read_json(inFile).loc[:, 0]
    
    rawData = rawString.drop(rawString.index[rawString == ''])\
                       .apply(lambda x: pd.Series(json.loads(x)))
    
    processedData = process_character_data(rawData)


    processedData.to_csv(outFile)
