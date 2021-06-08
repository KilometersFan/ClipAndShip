import os
import sys
import time
import json
import random
import configparser
import pandas as pd
import numpy as np
from pprint import pprint

def get_class_weight(df, categories):
    class_weight = {}
    for num, col in enumerate(categories):
        if num not in class_weight:
            class_weight[col] = round(rootdf[rootdf[col] == 1][col].sum() / rootdf.shape[0] * 100, 2)
    return class_weight

if __name__ == "__main__":
    print("Enter the ID of the channel you want to upsample")
    channel_id = "59635827" # input()

    start = time.time()
    print(f"Starting upsampling process at {start} for channel {channel_id}")

    if not os.path.exists("config/channels.ini"):
        print("Channels config file not found. Quitting...")
        sys.exit()

    cfg = configparser.ConfigParser()
    cfg.read("config/channels.ini")
    categories = cfg.options(channel_id)
    categoriesMap = {}
    if channel_id not in cfg.sections():
        print("Channel ID is not in channel config file. Quitting...")
        sys.exit()
    for option in cfg.options(channel_id):
        emoteList = cfg[channel_id][option].split(",")
        categoriesMap[option] = emoteList
    pprint(categoriesMap)

    rootdir = f"data/channels/{channel_id}"
    columns = ["text"]
    columns.extend(categories)
    print(columns)
    dfs = []
    avg_group_size = 0
    video_count = 0
    for file in os.listdir(rootdir):
        d = os.path.join(rootdir, file)
        if os.path.isdir(d):
            print(d)
            video_count += 1
            if os.path.exists(f"{d}/data.csv"):
                df = pd.read_csv(f"{d}/data.csv")
                dfs.append(df)
            if os.path.exists(f"{d}/data.json"):
                with open(f"{d}/data.json", "r") as ifile:
                    data = json.load(ifile)
                    avg_group_size += data["avgSize"]
    avg_group_size //= video_count

    rootdf = pd.concat(dfs, join="inner")
    pprint(rootdf.shape)
    pprint(rootdf)

    class_weights = get_class_weight(rootdf, categories)
    total_weight = sum(class_weights.values())
    print(f"Total class weight: {total_weight}")
    print(class_weights)
    imbalanced_classes = set()
    for category in categories:
        if class_weights[category]/total_weight < 1.0/(len(categories)):
            imbalanced_classes.add(category)
    print(imbalanced_classes)
    # Load recommendation data
    if not os.path.exists(f"data/channels/{channel_id}/recommendation_data.json"):
        print(f"Recommendation data file not found for {channel_id}. Quitting...")
    with open(f"data/channels/{channel_id}/recommendation_data.json", "r") as ifile:
        chain = json.load(ifile)
    categoryCount = len(imbalanced_classes)
    while categoryCount > 0:
        for category in imbalanced_classes:
            for j in range(5):
                sampledData = []
                for i in range(random.randrange(avg_group_size//2, avg_group_size)):
                    emote = random.choice(categoriesMap[category])
                    sums = {}
                    for key in chain[emote].keys():
                        sums[key] = float(sum(chain[emote].values()))
                    for key in chain[emote].keys():
                        chain[emote][key] = chain[emote][key]/sums[key]

                    data = np.random.choice(list(chain[emote].keys()), 1, p=list(chain[emote].values()))
                    newData = [emote, data[0]]
                    sampledData.extend(newData)
                # create text column value
                upsampledText = " ".join(sampledData)
                upsampledRow = [upsampledText]
                for existingCategory in sorted(categories):
                    upsampledRow.append(1 if existingCategory == category else 0)
                rootdf.loc[len(rootdf)] = upsampledRow
                new_class_weights = get_class_weight(rootdf, categories)
                new_total_weight = sum(new_class_weights.values())
                newImbalancedCount = 0
                for imbalanced_category in imbalanced_classes:
                    if (new_class_weights[imbalanced_category] / new_total_weight) < (1.0 / (len(categories))):
                        newImbalancedCount += 1
                categoryCount = newImbalancedCount
    rootdf.to_csv(f"data/channels/{channel_id}/upsampled_data.csv",index=False)
    print(f"New shape of data: {rootdf.shape}")
    final_class_weights = get_class_weight(rootdf, categories)
    final_total_weight = sum(final_class_weights.values())
    print(f"Final total class weight: {final_total_weight}")
    print(final_class_weights)
    end = time.time()
    print(f"Finished creating upsampled data for {channel_id} at {end}. Process took {end-start} seconds.")

