let channelId;
let videoResults;
$(document).ready(function () {
    eel.validBot()(function (valid) {
        invalid = true;
        while (invalid) {
            if (valid == true) {
                invalid = false;
                let searchParams = new URLSearchParams(window.location.search);
                if (searchParams.has("channel") && searchParams.get("channel") && searchParams.has("video") && searchParams.get("video")) {
                    let channel = parseInt(searchParams.get("channel"));
                    let video = searchParams.get("video");
                    channelId = channel;
                    $("#channelBtn").prop("href", "channel.html?id=" + channelId);
                    $("#videoBtn").prop("href", "video.html?id=" + channelId);
                    $("#vod").attr("src", "https://player.twitch.tv/?video=" + video + "&parent=localhost&time=0h0m0s&autoplay=false");
                    $("#vod").attr("width", $("#currentCategory").width())
                    eel.getChannel(channel)(function (info) {
                        eel.getVideoResults(channelId, video)(function (results) {
                            videoResults = results;
                            const categories = Object.keys(results);
                            for (let i = 0; i < categories.length; i++) {
                                let option = $("<option>", { "value": categories[i] });
                                option.text(categories[i]);
                                $("#currentCategory").append(option);
                            }
                            for (let j = 0; j < results[categories[0]].length; j++) {
                                let start = results[categories[0]][j].start
                                let end = results[categories[0]][j].end
                                let timeOption;
                                if (!j) {
                                    timeOption = $("<option>", { "value": start, "selected": "selected" });
                                }
                                else {
                                    timeOption = $("<option>", { "value": start });
                                }
                                timeOption.text(start + "-" + end);
                                $("#currentCategoryTime").append(timeOption);
                            }
                            $("#loading").hide();
                        });
                    });
                }
                else {
                    $("#channelVideoTitle").html("Error: In valid request parameters.")
                }
            }
            else {
                eel.initClipBot();
                invalid = !eel.validBot();
            }
        }
    });
});
$("#currentCategory").change(function () {
    let category = $("#currentCategory option:selected").text();
    if (category in videoResults) {
        let timestamps = videoResults[category];
        $("#currentCategoryTime").empty();
        for (let i = 0; i < timestamps.length; i++) {
            let start = timestamps[i].start
            let end = timestamps[i].end
            let timeOption = $("<option>", { "value": start });
            timeOption.text(start + "-" + end);
            $("#currentCategoryTime").append(timeOption);
        }
    }
});
$("#currentCategoryTime").change(function () {
    let timestamp = $("#currentCategoryTime").val();
    let src = $("#vod").attr("src");
    let timeIndex = src.indexOf("&time=");
    if (timeIndex >= 0) {
        src = src.substring(0, timeIndex) + "&time=" + timestamp + "&autoplay=true";
    }
    else {
        src += "&time=" + timestamp + "&autoplay=true";
    }
    $("#vod").attr("src", src);
});
$("#next").click(function () {
    let currTimeStamp = $("#currentCategoryTime option:selected");
    currTimeStamp.prop("selected", false);
    if (currTimeStamp.next().length > 0) {
        currTimeStamp.next().prop("selected", true);
        $("#currentCategoryTime").trigger("change");
    }
    else {
        $("#currentCategoryTime option").first().prop("selected", true);
        $("#currentCategoryTime").trigger("change");
    }
});
$("#prev").click(function () {
    let currTimeStamp = $("#currentCategoryTime option:selected");
    currTimeStamp.prop("selected", false);
    if (currTimeStamp.prev().length > 0) {
        currTimeStamp.prev().prop("selected", true);
        $("#currentCategoryTime").trigger("change");
    }
    else {
        $("#currentCategoryTime option").last().prop("selected", true);
        $("#currentCategoryTime").trigger("change");
    }
});
$("#playSelected").click(function () {
    let currTimeStamp = $("#currentCategoryTime option:selected");
    $("#currentCategoryTime").trigger("change");

});