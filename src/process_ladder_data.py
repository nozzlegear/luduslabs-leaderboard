import pandas as pd
import sys
import json

COLUMNS = ['id', 'name', 'realm', 'faction', 'rank', 'rating',
           'played', 'won', 'lost']


def process_character_field(character):
    return pd.Series([character['name'], character['realm']['slug']],
                     index=['name', 'realm'])


def process_ladder_data(raw):
    processed = pd.DataFrame(index=raw.index, columns=COLUMNS)
    processed.loc[:, 'id'] = raw.character.apply(lambda x: x['id'])
    processed.loc[:, ['name', 'realm']] = raw.character\
                                             .apply(process_character_field)
    
    processed.loc[:, 'faction'] = raw.faction.apply(lambda x: x['type'])
    processed.loc[:, ['played', 'won', 'lost']] = raw.season_match_statistics\
                                                     .apply(lambda x:pd.Series(x))
    
    processed.loc[:, ['rank', 'rating']] = raw.loc[:, ['rank', 'rating']]

    return processed


if __name__ == "__main__":

    inData = sys.argv[1]
    outData = sys.argv[2]

    with open(inData, 'r') as f:
        dataTemp = json.load(f)
        
    rawData = pd.DataFrame(dataTemp['entries'])

    processedData = process_ladder_data(rawData)

    processedData.to_csv(outData)
