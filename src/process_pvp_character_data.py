import pandas as pd
import numpy as np
import sys
import json

PVP_COLS = ['2v2_wins', '2v2_losses', '2v2_played', '2v2_rating',
            '3v3_wins', '3v3_losses', '3v3_played', '3v3_rating',
            'rbg_wins', 'rbg_losses', 'rbg_played', 'rbg_rating']

INDEX = ['id', 'name', 'realm', 'bracket', 'rating', 'season_played',
         'season_won', 'season_lost', 'week_played', 'week_won', 'week_lost',
         'season_id']

def process_line(x):
    if '"code":40' in x or x == '' or x == 'Internal Server Error':
        return pd.Series(index=INDEX)

    try: 
        z = json.loads(x)
    except:
        import pdb; pdb.set_trace()

    pvpData = pd.Series([z['character']['id'],
                         z['character']['name'],
                         z['character']['realm']['slug'],
                         z['bracket']['type'],
                         z['rating'],
                         z['season_match_statistics']['played'],
                         z['season_match_statistics']['won'],
                         z['season_match_statistics']['lost'],
                         z['weekly_match_statistics']['played'],
                         z['weekly_match_statistics']['won'],
                         z['weekly_match_statistics']['lost'],
                         z['season']['id']],
                        index=INDEX)

    return pvpData

def group_brackets(x):
    slug = {'BATTLEGROUNDS': 'rbg',
            'ARENA_2v2': '2v2',
            'ARENA_3v3': '3v3'}

    data = []
    for k in x.index:
        z = x.loc[k, :]
        bracket = slug[z['bracket']]
        cols = [bracket + '_' + k for k in z.index]

        data.append(pd.Series(z.values, index=cols))

    return pd.concat(data)

def get_season(x):
    z = x[['2v2_season_id', '3v3_season_id', 'rbg_season_id']]
    return z[~z.isnull()].iloc[0]

if __name__ == "__main__":

    rawData = pd.read_json(sys.argv[1])[0]
    rawData = rawData[~rawData.str.contains('"code":40')]
    processedLines = rawData.apply(process_line)
    groupedData = processedLines.groupby(['name', 'realm', 'id'])
    Z = groupedData.apply(group_brackets).reset_index().drop_duplicates()

    Zdeduped = Z.groupby(['name','realm','id'])\
                .apply(lambda x:x.drop_duplicates(subset=['level_3'], keep='last'))

    pivoted = Zdeduped.pivot(index=['name', 'realm', 'id'], columns='level_3',
                      values=0)

    DROP_COLS = [bracket+'_'+col for bracket in ['2v2','3v3','rbg']
                 for col in ['id','name','realm','bracket']]
    df = pivoted.drop(DROP_COLS, axis=1)
    nanIndex = pd.isnull(df.index.get_level_values(2))
    
    #df.loc[:, 'season_id'] = pivoted.apply(get_season, axis=1)

    df.loc[~nanIndex, :].to_csv(sys.argv[2])
