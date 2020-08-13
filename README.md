# TwitchClipAnalyzer
A desktop app that lets you sift through Twitch VODs for clips based on categories of emotes set by you. Perfect for content creators and streamers who want to make videos from stream footage and don't want to manually go through VODs to find the right footage.

# Features
- Search for and add channels you want to analyze.
- Create custom categories based on a channel's native Twitch emotes, Better TTV emotes, and FrankerFaceZ emotes.
- Find the latest 9 VODs for a channel or search for a VOD in particular. 
- Analyze a channel's VOD and get a list of clips for each category you created.
- Watch all the clips analyzed from a VOD with ease to determine which timestamps you want to use for your video.

# Requirements
- Windows 10. Currently I've only tested it on PC, so Mac will not be supported. However getting the .dmg file for Mac is a top priority.
- Google Chrome. This app basically creates a new window in Chrome to display the different pages. You can think of it as hosting your own website for your own use.

# Limitations
- Everything is stored locally. All analysis, channel categories, and channel info is on your machine, not on the cloud. Hopefully you have a beefy computer, but if you make videos, you probably have a lot of storage already. Still, be aware of this.
- Similarly, analysis performance is based on your machine. A computer with more cores and a fast processor will run analysis faster than a worse machine.
- Reliance on third party technologies. This app uses BTTV, FrankerFaceZ, and Twitch APIs. If any of these companies change something to their API the app may not work correctly. In that case, please report problems on the issues page.
- The Twitch API isn't very fleshed out and there are a lot of features that I wanted but aren't implemented yet. Also there are some features that just don't work. For instance, sometimes you search for a VOD that appears on a channel page on the Twitch website, but the Twitch API can't find it. Unfortuantely I can't do anything about those type of errors.

Feel free to ask questsions or report bugs on the issues page. If you enjoy the app, please spread the word! I want to make it easier for content creators to do their job. I watch those highlight videos too after all.
