---
layout: single
title: Clip & Ship
author_profile: true
header: 
    overlay_image: assets/images/logo_banner_textless.png
    overlay_filter: 0
---
## What is Clip & Ship?
_Clip it and ship it!_

Are you a content creator or editor? Do you hate keeping track of or scouring through 
VODs for notable moments during a broadcast? Are you tired of downloading 
entire VODs to get the footage you want? Then you need Clip & Ship!

Clip & Ship is a standalone application that enables content creators and Twitch streamers
to quickly find specific types of moments during their broadcast by analyzing
emote usage within a VOD. 

## Features

With Clip & Ship you can: 
- Create/Edit/Remove categories based on a streamers Twitch/BTTV/FFZ/other emotes.
  (ex: a "funny" category might include emotes like ![LULW](https://cdn.frankerfacez.com/emoticon/139407/1), 
  ![OMEGALUL](https://cdn.frankerfacez.com/emoticon/128054/1), 
  ![peepoGiggles](https://cdn.betterttv.net/emote/5e0bcf69031ec77bab473476/1x), etc).
- Process a streamer's VOD to find the best moments for each category.
- View processed moments in the app VOD player and see detailed statistics on emote usage during the moment.
- Download any of the moments found during processing.
- Download other moments by specifying the start & end time.
- Download the whole VOD.
- Export the list of processed moments to a CSV file.

## Install
Clip & Ship currently is supported on Mac OS and comes in several bundles.

To download as an app (preferred method), click [here][1]

To download as an executable with the console, click [here][2]

To download as a folder (to see the code/bundled packages), click [here][3].

You will also need to download and install [ffmpeg][4] in order to download clips/vods. 

When running as an executable with console or as a folder, you can install ffmpeg with [Homebrew][4]

When running as an app, find the ffmpeg download in [here][https://evermeet.cx/ffmpeg/] 
Make sure to download the zip file under the "FFmpeg" section. Extract the zip file and copy or move the `ffmpeg` executable in the same folder as the Clip & Ship app.

[1]:{{ site.url }}/downloads/app.zip
[2]:{{ site.url }}/downloads/console.zip
[3]:{{ site.url }}/downloads/folder.zip
[4]:https://brew.sh/
[5]:https://evermeet.cx/ffmpeg/

## Why Clip & Ship?

### It's Free
No upfront or subscription costs. Compared to similar services like 
[Highlight Play](https://highlightplay.com/) that have monthly fees, 
Clip & Ship is **the** cost-effective service to use.

### It's Smart
No other service can help you find specific types of moments.

### It's Fast
Instead of going through hours of footage, you can use Clip & Ship and 
have a list of notable moments ready in minutes. With tech from 
[twitch-dl](https://github.com/ihabunek/twitch-dl), downloads are lighting quick.

### It's Efficient
Clip & Ship supports parallel processing, so you can process multiple VODs simultaneously.

### It's Space-Saving
Only download what you need. No need to download a 6-hour long VOD just
to grab 10 minutes of footage.

### It's Open Source
The Clip & Ship source code is publicly available, meaning anyone can
analyze the workflow, verify no malicious code is present, and suggest
improvements to maintain Clip & Ship's integrity and efficiency. 

## Tradeoffs

### Everything's Local
Server costs and cloud storage is expensive, and I didn't receive funding 
for this project to pay for those services. So, Clip & Ship runs entirely 
on your machine and uses up your storage. But, that Clip & Ship is running 
locally is why it is free and open source.

### Reliance on APIs and third-party packages
Clip & Ship heavily relies on outside tech to function. The APIs used are
Twitch, BTTV, and FFZ to grab emote data for a channel. If **any** of these
APIs change or fail, Clip & Ship may not work. Similarly, Clip & Ship uses
the [twitch-python](https://github.com/PetterKraabol/Twitch-Python) package 
to grab information about and videos of a channel. If that breaks, so does 
Clip & Ship. 

## Bug Reports & Contributions

Found a bug and want to report it? Like the project and want to contribute?
Head over to the [GitHub](https://github.com/KilometersFan/ClipAndShip) page.
Create new issues for bugs and fork the repo and create a pull request for
contributions.

## Local Development

Install the required libraries listed in `requirements.txt`. 

To build everything as a script change directory to `src` and run `python3 clipnship.py`. To run the data_exporter program, run `python3 data_exporter.py` in the same directory. The upsampler will only work if you processed at least one video for the specified channel.

To build everything into one folder use the `clip&ship_dir.spec` file. First you must change the second value in the `pathex` array to the absolute path of the `src` directory of the repo, and the first value of the first tuple in the `datas` array to the location of the `eel.js` file (which is probably in your python `site-packages` directory), Run `pyinstaller clip&ship_dir.spec` in the src directory. 

To build everything into an executable with a console (just the `clipnship.exe` file), repeat the same steps above but with the `clip&ship_console.spec` file.

To build everything into an app, repeat the same steps above but with the `clip&ship_app.spec` file.

Add the `--noconfirm` flag to skip the confirmation prompt that asks if you want to delete the dist folder's contents. 
