# Clip & Ship
![clipnship_](https://user-images.githubusercontent.com/35278719/123028171-dc9f1b00-d393-11eb-80ff-44aa4c559361.png)
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
  ![peepoGiggle](https://cdn.betterttv.net/emote/5e0bcf69031ec77bab473476/1x), etc).
- Process a streamer's VOD to find the best moments for each category.
- View processed moments in the app VOD player and see detailed statistics on emote usage during each moment.
- Download moments found during processing.
- Download other moments by specifying the start & end time.
- Download an entire VOD.
- Export the list of processed moments to a CSV file.
- Upsample the data to even out category weights if imbalance occurs with the data_exporter.py file.

## Install

### Requirements
1. Supported web browser. For macOS users, you need Google Chrome. Windows users need Microsoft Edge.
    - These broswers are required because `python-eel`, the tool used to build the UI, only officially supports these browsers.
2. [ffmpeg][4] a framework that, among other things, allows users to download video streams. 

### Instructions
Clip & Ship currently is supported on both macOS and Windows but can be downloaded as an app on macOS only, (see [Tradeoffs](#tradeoffs) for more info).
For both Windows and macOS, Clip & Ship can be installed as an executable with a console, and as a folder with an executable.

These bundles are available to download at this Google Drive [link][1]. The `app.zip` file is the preferred method of install for macOS.

You will also need [ffmpeg][4] in order to download clips/vods. Each bundle comes with an `ffmpeg` executable, but if you want to download it from the source visit the `ffmpeg` downloads page [here][3].

If downloading `ffmpeg`, make sure to download the zip file under the "FFmpeg" section. Extract the zip file and copy or move the `ffmpeg` executable in the ***same*** folder as the Clip & Ship app/executable.

If on macOS you then need to give permission to your `ffmpeg` executable before you can run it since it's from the internet. 
This can be done via the terminal using `sudo chmod +x /path/to/Clip & Ship folder/ffmpeg` or by clicking the exe and giving permission in the corresponding prompt.

For local development, you need to install `ffmpeg` with [Homebrew][2] if on macOS or if on Windows, follow the instructions 
[here](https://video.stackexchange.com/questions/20495/how-do-i-set-up-and-use-ffmpeg-in-windows) or install it through 
[Chocolatey](https://chocolatey.org/).

[1]:https://drive.google.com/drive/folders/1ezPO_5EmMOlqLagOl5KOLWunkLthpnDH?usp=sharing
[2]:https://brew.sh/
[3]:https://evermeet.cx/ffmpeg/
[4]:https://ffmpeg.org/

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

### It's Honest
Clip & Ship isn't secretly selling your data, using your clicks for advertisement fraud, 
or doing anything other than what's listed above.

## Tradeoffs

### Chat Based Algorithm
To detect moments during a broadcast, Clip & Ship analyzes the chat for higher than
average comment rate and emote usage. VODs that have nonactive chats
and/or chats that don't use emotes will not get accurate results.

### Everything's Local
Servers and cloud storage are expensive, and I decided to develop this project
free of charge. So, how fast Clip & Ship runs is entirely up to your machine and 
as you will fill up your storage as process videos and download clips.But that Clip & Ship is running locally is why it 
is free and open source.

### Not a Website
As mentioned previously, Clip & Ship was built as a standalone app because
of the lack of funds to properly build and maintain a website. Downloading anything
from the internet can be dangerous, which is why the source code is available and 
the app can be verified independently by other programmers and cybersecurity experts.

### WIP Codebase
Clip & Ship was started early on in my programming career when I was experimenting with new
technologies and methodologies. Even though I spent the summer of 2021 refactoring and cleaning up
a lot of the code, there is still much I would like to improve (mostly the front end). As such,
there may be some workflows or functions that are messy or can be improved on. If you see any,
feel free to make a new issue and/or make a pull request with a fix!

### More Initial Setup
Unlike a website or other standalone desktop applications, 
Clip & Ship can't be run out of the box; Users must get 
their own Twitch API credentials and download/install/give
permission to ffmepg. 

### Reliance on APIs and third-party packages
Clip & Ship heavily relies on outside tech to function. The APIs used are
Twitch, BTTV, and FFZ to grab emote data for a channel. If **any** of these
APIs change or fail, Clip & Ship may not work. Similarly, Clip & Ship uses
the [twitch-python](https://github.com/PetterKraabol/Twitch-Python) package 
to grab information about and videos of a channel. If that breaks, so does 
Clip & Ship. 

### No Windows App Support
Currently, Clip & Ship **cannot** be run as an app on Windows due to a bug during the build process. A solution is ongoing
but feel free to use Clip & Ship in the other two bundle types (signified by the `_win` suffix).

## Example
### Setup
<img width="1273" alt="Screen Shot 2021-07-18 at 3 02 56 PM" src="https://user-images.githubusercontent.com/35278719/126083421-0885c6ea-30c7-43a3-b5b4-53aab5d65344.png">

### Adding a Channel
<img width="1273" alt="Screen Shot 2021-07-18 at 3 03 27 PM" src="https://user-images.githubusercontent.com/35278719/126083434-93de4d48-a36b-4f94-b9d7-6d125699a689.png">

### Viewing the Channel Settings
<img width="1273" alt="Screen Shot 2021-07-18 at 3 04 00 PM" src="https://user-images.githubusercontent.com/35278719/126083455-e7c8fd02-b8f4-4d54-a01b-26c110fba321.png">

### Adding a Category
<img width="1274" alt="Screen Shot 2021-07-18 at 3 04 36 PM" src="https://user-images.githubusercontent.com/35278719/126083471-033ab71e-c684-4327-861d-4aa6a47aa94f.png">
<img width="1274" alt="Screen Shot 2021-07-18 at 3 05 09 PM" src="https://user-images.githubusercontent.com/35278719/126083484-d3301050-aab2-40a9-b536-74d193ae80a5.png">

### Viewing a Channel's VODs
<img width="1275" alt="Screen Shot 2021-07-18 at 3 05 38 PM" src="https://user-images.githubusercontent.com/35278719/126083508-2ec7154a-0a84-4490-af98-2f9b93ad6dee.png">

### Processing a VOD
<img width="1274" alt="Screen Shot 2021-07-18 at 3 06 21 PM" src="https://user-images.githubusercontent.com/35278719/126083537-de6520e9-3920-4fa7-928f-10f54b33b728.png">
<img width="1276" alt="Screen Shot 2021-07-18 at 3 06 30 PM" src="https://user-images.githubusercontent.com/35278719/126083542-c53bb6bf-3826-4438-bd58-45ed6c9b6ab0.png">

### Finishing VOD Processing
<img width="1275" alt="Screen Shot 2021-07-18 at 3 08 54 PM" src="https://user-images.githubusercontent.com/35278719/126083600-988e2f58-5105-4f24-9ce5-e760420311b5.png">

### Viewing VOD Results
<img width="1274" alt="Screen Shot 2021-07-18 at 3 09 22 PM" src="https://user-images.githubusercontent.com/35278719/126083618-aedc8fb9-4dc2-4a1f-9cdd-940f36396c03.png">
<img width="1274" alt="Screen Shot 2021-07-18 at 3 09 41 PM" src="https://user-images.githubusercontent.com/35278719/126083630-b60dbe31-7d9a-4727-8b4f-a600866a17dd.png">

### Downloading a Clip
<img width="1272" alt="Screen Shot 2021-07-18 at 3 10 11 PM" src="https://user-images.githubusercontent.com/35278719/126083643-0a9114b0-efd9-418f-8558-7cd9648409dc.png">
<img width="1261" alt="Screen Shot 2021-07-18 at 3 10 25 PM" src="https://user-images.githubusercontent.com/35278719/126083649-e268b749-8232-4ff3-b5f5-eb04116716f5.png">


## Bug Reports & Contributions

Found a bug and want to report it? Like the project and want to contribute?
Head over to the [GitHub](https://github.com/KilometersFan/ClipAndShip) page.
Create new issues for bugs and fork the repo and create a pull request for
contributions.

## Local Development
NOTE: These instructions are written for macOS, so if you are building on Windows, substitute the `.spec`
files mentioned below for the Windows versions, suffixed with `_win`.

Install the required libraries listed in `requirements.txt` (virtual environment recommended). 

To build everything as a script change directory to `src` and run `python3 clipnship.py` (or just `python clipnship.py` if you only have Python 3 installed). To run the data_exporter program, run `python3 data_exporter.py` in the same directory. The upsampler will only work if you processed at least one video for the specified channel.

To build everything into one folder use the `clip&ship_folder.spec` file. I used a virtual environment called `clipandship`, and you will see that in the `pathex` array that there are several tuples with the first value referencing some package in `clipandship`. If you use a virtual environment, I'd recommend also naming it `clipandship` so you don't have to change anything. If you don't use one, or call yours something else, you will have to replace all the values that look at `clipandship` to wherever your packages are stored. When you are finished, run `pyinstaller clip&ship_folder.spec` in the src directory. 

To build everything into an executable with a console (just the `clipnship` executable file), repeat the same steps above but with the `clip&ship_console.spec` file.

To build everything into an app, repeat the same steps above but with the `clip&ship_app.spec` file. You will also need to uncomment and comment some lines of code regarding file paths. 
The changes are described on:

1. src/twitchdl/command.py line 54
2. src/clipnship.py lines 31-34, 476
3. src/models/util.py line 14

Add the `--noconfirm` flag to skip the confirmation prompt that asks if you want to delete the `dist/` folder's contents. 

