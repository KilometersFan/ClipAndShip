let channelId;
let videoId;
let videoResults;
let categories;
let selectedCategories;
let selectedRow;
let filteredResults;
let currentTimeStamp;
let dirChoice = 1;
let sortChoice = "start";
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})
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
                    videoId = video;
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
$("#asc").click(function() {
    $("#dirChoice").text("ASC");
    dirChoice = 1;
    $(`#${sortChoice}`).trigger("click");
});
$("#desc").click(function() {
    $("#dirChoice").text("DESC");
    dirChoice = 0;
    $(`#${sortChoice}`).trigger("click");
});
$("#length").click(function() {
    $("#sortChoice").text("Length");
    sortChoice = "length"
    if (dirChoice == 1) {
        filteredResults = filteredResults.sort((groupA, groupB) => groupA["length"] - groupB["length"]);
    }
    else {
        filteredResults = filteredResults.sort((groupA, groupB) => groupB["length"] - groupA["length"]);
    }
    populateTable(filteredResults);
});
$("#start").click(function() {
    $("#sortChoice").text("Start");
    sortChoice = "start";
    if (dirChoice == 1) {
        filteredResults = filteredResults.sort((groupA, groupB) => groupA["start"] - groupB["start"]);
    }
    else {
        filteredResults = filteredResults.sort((groupA, groupB) => groupB["start"] - groupA["start"]);
    }
    populateTable(filteredResults);
});
$("#similarity").click(function() {
    $("#sortChoice").text("Similarity");
    sortChoice = "similarity";
    if (dirChoice == 1) {
        filteredResults = filteredResults.sort((groupA, groupB) => Math.max.apply(Math, Object.values(groupA["similarities"])) - Math.max.apply(Math, Object.values(groupB["similarities"])));
    }
    else {
        filteredResults = filteredResults.sort((groupA, groupB) => Math.max.apply(Math, Object.values(groupB["similarities"])) - Math.max.apply(Math, Object.values(groupA["similarities"])));
    }
    populateTable(filteredResults);
});
$("#csvExport").click(function() {
    let csvData = $.map(filteredResults, (obj) => $.extend(true, {}, obj));
    csvData.forEach((group) => {
        group["start"] = createTimestamp(group["start"]);
        group["end"] = createTimestamp(group["end"]);
        let groupSimilarities = []
        Object.keys(group["similarities"]).forEach((key) => {
            groupSimilarities.push(`${key}:${group["similarities"][key]}`);
        });
        group["similarities"] = groupSimilarities.join(" ");
        delete group.img;
        delete group.emoteFrequency;
    });

    eel.csvExport(videoId, csvData);
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

function populateTable (defaultFilteredResults=null) {
    $("#resultBody").empty();
    let i = 1;
    if (defaultFilteredResults) {
        filteredResults = defaultFilteredResults;
    }
    else if (selectedCategories.size > 0) {
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
            eel.getGraph(group["graph_data"])(function (graph) {
                $("#groupChart").attr("src", `data:image/png;base64, ${graph}`)
            });
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