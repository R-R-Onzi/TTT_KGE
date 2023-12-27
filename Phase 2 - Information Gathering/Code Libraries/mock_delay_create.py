import pandas as pd
import cv2 as cv 
import numpy as np
import argparse
from os import walk
import math
from collections import defaultdict
import itertools
import random


def main(path):

    df_trip = pd.read_csv(f"{path}/trip_results.csv")
    all_ids = []
    final_rez: defaultdict = defaultdict(list)
    for i in range(df_trip["trip_id"].size):
        all_ids.append(df_trip["trip_id"][i])
        
    id_gen = 0
    for id in all_ids:
        predicted = random.gauss(60, 30)
        actual = random.gauss(60, 30)
        
        final_rez['delay_id'].append(id_gen)
        final_rez['trip_id'].append(id)
        final_rez['predicted_delay'].append(predicted)
        final_rez['actual_delay'].append(actual)
        id_gen += 1
    pd.DataFrame(final_rez).to_csv("mock_delay.csv", index=False)       


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', metavar='path', required=True,
    help='folder points')
    
    args = parser.parse_args()
    

    main(args.folder)

    # folder for me = /home/rubs/Documents/code/TTT_KGE/Phase 2 - Information Gathering/Code Libraries/Data