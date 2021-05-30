let channelId;
let videoResults;
let categories;
let selectedCategories;
let selectedRow;
let filteredResults;
let currentTimeStamp;
$(document).ready(function () {
    selectedCategories = new Set();
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
                    $("#channelBtn").prop("href", `channel.html?id=${channelId}`);
                    $("#videoBtn").prop("href", `video.html?id=${channelId}`);
                    $("#vod").attr("src", `https://player.twitch.tv/?video=${video}&parent=localhost&time=0h0m0s&autoplay=false`);
                    $("#vod").attr("width", $("#currentCategory").width())
                    eel.getChannel(channel)(function (info) {
                        categories = info["categories"];
                        categories.forEach((category) => {
                            let btn = $("<button>", {"class": "btn btn-secondary"});
                            btn.text(category);
                            btn.value = category;
                            btn.click(function() {
                                if (btn.hasClass("btn-secondary")) {
                                    btn.removeClass("btn-secondary");
                                    btn.addClass("btn-primary");
                                    selectedCategories.add(btn.value);
                                }
                                else if (btn.hasClass("btn-primary")) {
                                    btn.removeClass("btn-primary");
                                    btn.addClass("btn-secondary");
                                    selectedCategories.delete(btn.value);
                                }
                                populateTable();
                            });
                            $("#categoryBtns").append(btn);
                        });
                        eel.getVideoResults(channelId, video)(function (results) {
                            videoResults = results;
                            populateTable();
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
$("#next").click(function () {
    if (!selectedRow) {
        return
    }
    let nextRow = selectedRow.next();
    if (nextRow.length == 0) {
        nextRow = $("#resultBody").children(":first");
    }
    nextRow.trigger("click");
    $("#playSelected").trigger("click");
});
$("#prev").click(function () {
    if (!selectedRow) {
        return
    }
    let prevRow = selectedRow.prev();
    if (prevRow.length == 0) {
        prevRow = $("#resultBody").children(":last");
    }
    prevRow.trigger("click");
    $("#playSelected").trigger("click");
});
$("#playSelected").click(function () {
    if (!selectedRow) {
        return
    }
    currentTimeStamp = $(`#${selectedRow.attr("id")} td:nth-child(3)`).text();
    let src = $("#vod").attr("src");
    let timeIndex = src.indexOf("&time=");
    if (timeIndex >= 0) {
        src = `${src.substring(0, timeIndex)}&time=${currentTimeStamp}&autoplay=true`;
    }
    else {
        src += `&time=${currentTimeStamp}&autoplay=true`;
    }
    $("#vod").attr("src", src);
});

function createTimestamp(seconds) {
    let hours = (seconds/3600>>0);
    let min = ((seconds/60) % 60 >>0)
    let sec = seconds % 60;
    timeStamp = `${hours}h${min}m${sec}s`;
    return timeStamp
}

function resultsFilter(group) {
    return Array.from(selectedCategories).some(category => Object.keys(group["similarities"]).includes(category));
}

function clearSelectedRowColor() {
    $(".tableRow").each(function() {
        if (selectedRow.attr("id") != $(this).attr("id")) {
            $(this).css("background-color", "");
        }
    });
}

function populateTable () {
    $("#resultBody").empty();
    let i = 1;
    if (selectedCategories.size > 0) {
        filteredResults = videoResults["groups"].filter(resultsFilter);
    }
    else {
        filteredResults = videoResults["groups"];
    }
    filteredResults.forEach((group) => {
        let row = $("<tr>", {"class": "tableRow", "id": i});
        row.hover(function() {
            $(this).css("cursor", "grab");
        });
        row.click(function() {
            $(this).css("background-color", "#33b1ff");
            selectedRow = $(this);
            clearSelectedRowColor();
            $("#groupChart").attr("src", `data:image/png;base64, ${group["img"]}`)
        })
        let groupId = $("<th>", {"scope": "row"});
        groupId.text(i);
        i++;
        let groupLength = $("<td>");
        groupLength.text(group["length"]);
        let groupStart = $("<td>");
        groupStart.text(createTimestamp(group["start"]));
        let groupEnd = $("<td>");
        groupEnd.text(createTimestamp(group["end"]));
        let groupCategories = $("<td>");
        let groupSimilarities = []
        Object.keys(group["similarities"]).forEach((key) => {
            groupSimilarities.push(`${key}: ${group["similarities"][key]}`);
        });
        groupCategories.css("white-space", "pre");
        groupCategories.text(groupSimilarities.join("\n\n"));
        row.append(groupId);
        row.append(groupLength);
        row.append(groupStart);
        row.append(groupEnd);
        row.append(groupCategories);
        $("#resultBody").append(row);
    });
}