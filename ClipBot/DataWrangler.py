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

def create_sample_data(category, categoriesMap, chain, start, end):
    sampledData = []
    for i in range(random.randrange(start), end):
        emote = random.choice(categoriesMap[category])
        sums = {}
        for key in chain[emote].keys():
            sums[key] = float(sum(chain[emote].values()))
        for key in chain[emote].keys():
            chain[emote][key] = chain[emote][key] / sums[key]

        data = np.random.choice(list(chain[emote].keys()), 1, p=list(chain[emote].values()))
        newData = [emote, data[0]]
        sampledData.extend(newData)
    return sampledData

if __name__ == "__main__":
    """
        Lets a user compile data for a channel into a CSV file for easy use.
        Upsampling of data for minority categories is provided.
    """
    print("Enter the ID of the channel you want to view")
    channel_id = input()

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

    columns = ["text"]
    columns.extend(categories)
    print(columns)
    rootdir = f"data/channels/{channel_id}"

    print("Do you want to upsample your data to even out any category imbalance? yes/no")
    isUpsample = input().lower()
    if isUpsample == "yes":
        print("Do you want to set a minimum number of data points? yes/no")
        hasMinimum = input().lower()
        if hasMinimum == "yes":
            print("Please enter the minimum number:")
            try:
                min_sample_count = int(input())
                if min_sample_count <= 0:
                    print("Value must be a positive number. Quitting...")
                    sys.exit()
            except ValueError as e:
                print("Value entered is not an integer. Quitting...")
                sys.exit()
        elif hasMinimum == "no":
            min_sample_count = -1
        else:
            print("Invalid answer provided. Quitting...")
            sys.exit()

        print("Do you want to create data that has multiple labels? yes/no")
        multiLabeledData = input().lower()
        if multiLabeledData == "yes":
            createMultiLabelData = True
        elif multiLabeledData == "no":
            createMultiLabelData = False
        else:
            print("Invalid answer provided. Quitting...")
            sys.exit()
        start = time.time()
        print(f"Starting upsampling process at {start} for channel {channel_id}")

        dfs = []
        avg_group_size = 0
        video_count = 0
        # calculate average group size
        for file in os.listdir(rootdir):
            d = os.path.join(rootdir, file)
            if os.path.isdir(d):
                video_count += 1
                if os.path.exists(f"{d}/data.csv"):
                    df = pd.read_csv(f"{d}/data.csv")
                    if set(columns) == set(df.columns.tolist()):
                        dfs.append(df)
                    else:
                        print(f"{d}/data.csv does not have the same categories as listed in the config file. Skipping...")
                if os.path.exists(f"{d}/data.json"):
                    with open(f"{d}/data.json", "r") as ifile:
                        data = json.load(ifile)
                        avg_group_size += data["avgSize"]
        avg_group_size //= video_count
        avg_group_size = int(avg_group_size)
        rootdf = pd.concat(dfs, join="inner")
        pprint(rootdf)

        class_weights = get_class_weight(rootdf, categories)
        total_weight = sum(class_weights.values())
        print(f"Total class weight: {total_weight}")
        print(class_weights)
        if not os.path.exists(f"data/channels/{channel_id}/recommendation_data.json"):
            print(f"Recommendation data file not found for {channel_id}. Quitting...")
        with open(f"data/channels/{channel_id}/recommendation_data.json", "r") as ifile:
            chain = json.load(ifile)
        imbalanced_classes = set()
        # Find imabalanced classed
        for category in categories:
            if class_weights[category]/total_weight < 1.0/(len(categories)):
                imbalanced_classes.add(category)
        print(imbalanced_classes)
        # create upsmapled data
        categoryCount = len(imbalanced_classes)
        while categoryCount > 0:
            for category in imbalanced_classes:
                sampledData = create_sample_data(category, categoriesMap, chain, avg_group_size * 2 // 3, avg_group_size)
                # create text column value
                upsampledText = " ".join(sampledData)
                upsampledRow = [upsampledText]
                for existingCategory in sorted(categories):
                    upsampledRow.append(1 if existingCategory == category else 0)
                rootdf.loc[len(rootdf)] = upsampledRow
                # Find new imbalanced classes
                new_class_weights = get_class_weight(rootdf, categories)
                new_total_weight = sum(new_class_weights.values())
                newImbalancedCount = 0
                for imbalanced_category in imbalanced_classes:
                    if (new_class_weights[imbalanced_category] / new_total_weight) < (1.0 / (len(categories))):
                        newImbalancedCount += 1
                categoryCount = newImbalancedCount
                print(f"New imbalanced count: {newImbalancedCount}")
            # check if we created more imbalance or we are under the minimum sample count, if so keep upsampling
            if categoryCount == 0:
                print("=================================")
                print(f"Category count is 0")
                last_class_weights = get_class_weight(rootdf, categories)
                print(last_class_weights)
                last_total_weight = sum(last_class_weights.values())
                print(f"New total: {last_total_weight}")
                lastImbalancedCount = 0
                new_imbalanced_classes = set()
                for category in categories:
                    if (last_class_weights[category] / last_total_weight) < (1.0 / (len(categories))):
                        new_imbalanced_classes.add(category)
                categoryCount = len(new_imbalanced_classes)
                imbalanced_classes = new_imbalanced_classes

                # check if # rows is >= minimum provided and when the initial imbalanced classes are upsampled
                if len(imbalanced_classes) == 0 and min_sample_count > 0:
                    if len(rootdf) < min_sample_count:
                        imbalanced_classes = set(categories)
                        categoryCount = len(categories)
                print(f"New imbalanced count (last): {categoryCount}")
                print(f"New imbalanced set: {imbalanced_classes}")
                print("######################################")
        # create multi labeled data if specified
        if createMultiLabelData:
            print("Starting process to craete multilabeled data")
            for category in categories:
                print(f"First category: {category}")
                for other_category in categories:
                    if category != other_category:
                        print(f"\tSecond category: {other_category}")
                        for j in range(5):
                            firstSampledData = create_sample_data(category, categoriesMap, chain, avg_group_size // 3, avg_group_size * 3 // 4)
                            secondSampleData = create_sample_data(other_category, categoriesMap, chain, avg_group_size // 3, avg_group_size * 3 // 4)
                            sampledData = firstSampledData + secondSampleData
                            upsampledText = " ".join(sampledData)
                            upsampledRow = [upsampledText]
                            for existingCategory in sorted(categories):
                                upsampledRow.append(1 if existingCategory == category or existingCategory == other_category else 0)
                            rootdf.loc[len(rootdf)] = upsampledRow
                print("======================================")

        rootdf.to_csv(f"data/channels/{channel_id}/upsampled_data.csv",index=False)
        print(f"New shape of data: {rootdf.shape}")
        final_class_weights = get_class_weight(rootdf, categories)
        final_total_weight = sum(final_class_weights.values())
        print(f"Final total class weight: {final_total_weight}")
        print(final_class_weights)
        end = time.time()
        print(f"Finished creating upsampled data for {channel_id} at {end}. Process took {end-start} seconds.")
    elif isUpsample == "no":
        start = time.time()
        print(f"Starting data combination process at {start} for channel {channel_id}")
        dfs = []
        for file in os.listdir(rootdir):
            d = os.path.join(rootdir, file)
            if os.path.isdir(d):
                if os.path.exists(f"{d}/data.csv"):
                    df = pd.read_csv(f"{d}/data.csv")
                    if set(columns) == set(df.columns.tolist()):
                        dfs.append(df)
                    else:
                        print(f"{d}/data.csv does not have the same categories as listed in the config file. Skipping...")
        rootdf = pd.concat(dfs, join="inner")
        pprint(rootdf)
        rootdf.to_csv(f"data/channels/{channel_id}/combined_data.csv", index=False)
        end = time.time()
        print(f"Finished data combination process at {start} for channel {channel_id} at {end}. Process took {end-start} seconds.")
    else:
        print("Invalid response. Quitting...")
        sys.exit()