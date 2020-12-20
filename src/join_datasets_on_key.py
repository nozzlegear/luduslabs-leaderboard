import sys
import pandas as pd

if __name__ == "__main__":

    inData1 = sys.argv[1]
    inData2 = sys.argv[2]
    key = sys.argv[3]
    outData = sys.argv[4]

    data1 = pd.read_csv(inData1)
    data2 = pd.read_csv(inData2)

    joinedDataset = data1.set_index(key).join(data2.set_index(key), rsuffix='_right')

    joinedDataset.to_csv(outData)
