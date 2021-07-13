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
let player;
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})
$(document).ready(function () {
    selectedCategories = new Set();
    eel.valid_bot()(function (valid) {
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
                    $("#channelVideoTitle").text(`Video ID: ${videoId}`);
                    $("#channelBtn").prop("href", `channel.html?id=${channelId}`);
                    $("#videoBtn").prop("href", `video.html?id=${channelId}`);
                    let options = {
                        width: "100%",
                        height: 650,
                        video: `${videoId}`,
                        autoplay: false,
                    };
                    player = new Twitch.Player("player", options);
                    eel.get_channel(channel)(function (info) {
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
                        eel.get_video_results(channelId, video)(function (results) {
                            videoResults = results;
                            console.log(videoResults);
                            populateTable();
                            $("#loading").hide();
                            if (videoResults["downloadedVOD"] === true){
                                $("#downloadVod").prop("disabled", true);
                                $("#downloadVod").click(function () {
                                    return;
                                })
                            }
                        });
                    });
                }
                else {
                    $("#channelVideoTitle").html("Error: In valid request parameters.")
                }
            }
            else {
                eel.init_clip_bot();
                invalid = !eel.valid_bot();
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

    eel.csv_export(videoId, csvData);
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
        return;
    }
    currentTimeStamp = $(`#${selectedRow.attr("id")} td:nth-child(3)`).text();
    console.log(currentTimeStamp);
    player.seek(parseSeconds(currentTimeStamp, true));
    player.play()
});
$("#downloadVod").click(function (){
    $("#downloadErr").text("");
    $("#downloadSuccess").text("");
    eel.download_vod(videoId);
    $(this).prop("disabled", true);
});
$("#downloadOther").click(function () {
    $("#downloadErr").text("");
    $("#downloadSuccess").text("");
    $("#downloadOther").prop("disabled", true);
    const start = $("#downloadOtherInputStart").val();
    const end = $("#downloadOtherInputEnd").val();
    if (start && end) {
        $("#downloadErr").text("");
        parsedStart = parseSeconds(start);
        parsedEnd = parseSeconds(end);
        if (parsedStart >= 0 && parsedEnd >= 0) {
            eel.download_clip(channelId, videoId, null, parseSeconds(start), parseSeconds(end));
        }
        else {
            $("#downloadErr").text("Start and/or End time(s) are invalid");
            $(this).prop("disabled", false);
        }
    }
    else {
        $(this).prop("disabled", false);
        $("#downloadOtherInputStart").val("");
        $("#downloadOtherInputEnd").val("");
        $("#downloadErr").text("Start and End times must both be specified");
    }
});
function parseSeconds(timestamp, isTwitchFormat=false) {
    let parts = [];
    if (!isTwitchFormat) {
        parts = timestamp.split(":");
    }
    else {
        let hoursIndex = timestamp.indexOf("h");
        let minutesIndex = timestamp.indexOf("m");
        let secondsIndex = timestamp.indexOf("s");
        parts.push(parseInt(timestamp.substring(0, hoursIndex)))
        parts.push(parseInt(timestamp.substring(hoursIndex + 1, minutesIndex)))
        parts.push(parseInt(timestamp.substring(minutesIndex + 1, secondsIndex)))
    }
    if (parts.length !== 3) {
        return -1;
    }
    const hours = parseInt(parts[0]);
    const minutes = parseInt(parts[1]);
    const seconds = parseInt(parts[2]);
    if (isNaN(hours) || isNaN(minutes) || isNaN(seconds)) {
        return -1;
    }
    if (hours < 0 || !(minutes <= 59 && minutes >= 0) || !(seconds <= 59 && seconds >= 0)) {
        return -1;
    }
    return hours * 3600 + minutes * 60 + seconds
}
function createTimestamp(seconds) {
    let hours = (seconds/3600>>0);
    let min = ((seconds/60) % 60 >>0)
    let sec = seconds % 60;
    let timeStamp = `${hours}h${min}m${sec}s`;
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
    if (filteredResults) {
        filteredResults.forEach((group) => {
            let row = $("<tr>", {"class": "tableRow", "id": `start-${group["start"]}-end-${group["end"]}`});
            row.hover(function() {
                $(this).css("cursor", "grab");
            });
            row.click(function() {
                $(this).css("background-color", "#33b1ff");
                selectedRow = $(this);
                clearSelectedRowColor();
                eel.get_graph(group["graph_data"])(function (graph) {
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
            let downloadCol = $("<td>", {"id": `start-${group["start"]}-end-${group["end"]}-download`});
            let downloadBtn = $("<button>", {"class": "btn btn-primary", "id": `start-${group["start"]}-end-${group["end"]}-btn`});
            downloadBtn.append($("<i>", {"class": "fa fa-download"}));
            let categories = Object.keys(group["similarities"]).join("_");
            if (videoResults["downloaded"].includes(`${group["start"]}-${group["end"]}`)) {
                downloadBtn.prop("disabled", true);
                downloadBtn.removeClass("btn-primary");
                downloadBtn.addClass("btn-secondary");
            }
            else {
                downloadBtn.click(function(e) {
                    $("#downloadErr").text("");
                    $("#downloadSuccess").text("");
                    eel.download_clip(channelId, videoId, categories, group["start"], group["end"]);
                    downloadBtn.empty()
                    downloadBtn.append($("<span>",
                        {"class": "spinner-border spinner-border-sm", "role": "status", "aria-hidden": "true"}));
                });
            }
            downloadCol.append(downloadBtn);
            row.append(groupId);
            row.append(groupLength);
            row.append(groupStart);
            row.append(groupEnd);
            row.append(groupCategories);
            row.append(downloadCol);
            $("#resultBody").append(row);
        });
    }
}