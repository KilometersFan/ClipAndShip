function createVideoCard(data, processing=true, channelId=null) {
    let col = $("<div>", { "class": "mb-2 mt-2 col-sm-8 col-md-6 col-lg-4 d-flex align-self-stretch", "id": data["id"] + "Div" });
    let card = $("<div>", { "class": "card custom-card", "id": data["id"] + "Card" });
    let img = $("<img>", { "src": data["thumbnail"], "alt": data["title"] });
    card.append(img)
    let cardBody = $("<div>", { "class": "card-body", "id": data["id"] + "Body" });
    let h5 = $("<h5>", { "class": "card-title" });
    h5.text(data["title"]);
    let p = $("<p>", { "class": "card-text" });
    p.text(data["desc"]);
    let date = $("<p>", { "class": "card-text" });
    date.text(data["date"]);
    let container = $("<div>", { "class": "d-flex justify-content-between", "id": data["id"] + "Container", "style": "display: block; width: 100%" });
    let btn;
    if (!processing) {
        btn = $("<button>", {
            "class": "btn action-btn mx-0", "value": data["id"], "data-toggle": "modal", "data-target": "#videoMessageModal"
        });
        btn.text("Process");
        btn.click(function () {
            $(`#${data["id"]}Div`).remove();
            eel.clip_video(parseInt(channelId), parseInt(data["id"]));
            setTimeout(updateProcessingVideos, 500);
        });
        let removeBtn = $("<button>", {
            "class": "btn delete-btn mr-1", "type": "button", "value": data["id"], "data-toggle": "modal", "data-target": "#videoRemoveModal"
        });
        removeBtn.text("Remove");
        removeBtn.click(function () {
            let videoToRmv = removeBtn.val();
            eel.remove_video(channelId, videoToRmv)(function (response) {
                if (response.success) {
                    $("#rmvBody").text("Successfully removed video from your list.")
                }
                else {
                    $("#rmvBody").text("Unable to remove video from your list.")
                }
                $(`#${data["id"]}Div`).remove();
            });
        });
        container.append(removeBtn);
        container.append(btn);
    }
    cardBody.append(h5);
    cardBody.append(p);
    cardBody.append(date);
    if (!processing) {
        let results = $("<a>", { "class": "btn btn-primary ml-1", "href": "results.html?channel=" + channelId + "&video=" + parseInt(data["id"]), "id": "results" + data["id"] });
        results.text("View Results");
        container.append(results);
    }
    card.append(cardBody);
    cardBody.append(container);
    col.append(card);
    return col;
}
function populateProcessingVideos(data) {
    console.log("Processing vids");
    console.log(data);
    let row = $("#processingVideoRow");
    row.empty();
    for (let i = 0; i < data.length; i++) {
        let videoCard = createVideoCard(data[i]);
        row.append(videoCard);
    }
    if (data.length == 0) {
        let noVideos = $("<p>", {"style": "padding-left: 15px"})
        noVideos.text("No processing videos found.");
        row.append(noVideos);
    }
    $(".loading").hide();
}
function populateUserVideos(data) {
    let row = $("#yourVideoRow");
    console.log(data);
    if (Object.keys(data).length == 0) {
        let noVideos = $("<p>", {"style": "padding-left: 15px", "id": "noUserVids"})
        noVideos.text("No user videos found.");
        row.append(noVideos);
    }
    else {
        let totalChannels = Object.keys(data).length;
        Object.keys(data).forEach((channelId) => {
            let videos = data[channelId];
            if (videos.length == 0) {
                totalChannels--;
            }
            eel.get_channel(parseInt(channelId))(function (info) {
                console.log(info);
                let channelCol = $("<div>", {"class": "col-sm-12"});
                let channelRow = $("<div>", {"class": "row", "id": info["id"] + "Row"});
                let channelContainer = $("<div>", {"class": "col-sm-12 d-flex align-items-center"});
                let channelName = $("<h3>", {"class": "p-2 mr-auto"});
                channelName.text(info["name"]);
                channelContainer.append(channelName);
                let channelVideos = $("<a>", {"class": "btn btn-primary p-2", "href": "video.html?id=" + channelId});
                channelVideos.text("Channel Videos");
                let channelSettings = $("<a>", {"class": "btn btn-secondary p-2 mr-2", "href": "channel.html?id=" + channelId});
                channelSettings.text("Channel Settings");
                channelContainer.append(channelSettings);
                channelContainer.append(channelVideos);
                channelRow.append(channelContainer);
                if (videos.length > 0) {
                    eel.get_videos(parseInt(channelId), videos)(function (response) {
                        for (let i = 0; i < response.length; i++) {
                            let videoCard = createVideoCard(response[i], false, channelId);
                            channelRow.append(videoCard);
                        }
                        channelCol.append(channelRow);
                        row.append(channelCol);
                    });
                }
            });
        });
        if (totalChannels == 0) {
            row.empty();
            let noVideos = $("<p>", {"style": "padding-left: 15px"})
            noVideos.text("No user videos found.");
            row.append(noVideos);
        }
    }
    $(".loading").hide();
}
function updateProcessingVideos() {
    eel.get_processing_videos()(function (data) {
        console.log(data);
        populateProcessingVideos(data);
    });
}
function updateUserVideos() {
    eel.get_user_videos()(function (data) {
        populateUserVideos(data);
    });
}
function addVideoCard(videoId, channelId) {
    if (!(channelId && videoId)) {
        return;
    }
    let processingRow = $("#processingVideoRow");
    let row = $("#yourVideoRow");
    if (processingRow.children().length == 0 ) {
        processingRow.empty();
    }
    eel.get_videos(parseInt(channelId), [videoId])(function (response) {
        if (!$(`#${channelId}Row`).length) {
            row.empty();
            console.log("Channel row not found");
            eel.get_channel(parseInt(channelId))(function (info) {
                let channelCol = $("<div>", {"class": "col-sm-12"});
                let channelRow = $("<div>", {"class": "row", "id": info["id"] + "Row"});
                let channelContainer = $("<div>", {"class": "col-sm-12 d-flex align-items-center"});
                let channelName = $("<h3>", {"class": "p-2 mr-auto"});
                channelName.text(info["name"]);
                channelContainer.append(channelName);
                let channelVideos = $("<a>", {"class": "btn btn-primary p-2", "href": "video.html?id=" + channelId});
                channelVideos.text("Channel Videos");
                let channelSettings = $("<a>", {"class": "btn btn-secondary p-2 mr-2", "href": "channel.html?id=" + channelId});
                channelSettings.text("Channel Settings");
                channelContainer.append(channelSettings);
                channelContainer.append(channelVideos);
                channelRow.append(channelContainer);
                channelCol.append(channelRow);
                row.append(channelCol);
                if (response[0]) {
                    console.log("Appending card to new row");
                    let newVideoCard = createVideoCard(response[0], false, channelId);
                    $(`#${channelId}Row`).append(newVideoCard);
                    $(`#${videoId}Body`).css("background-color", "#17a2b8");
                }
            });
        }
        else {
            if (response[0]) {
                console.log("Appending card to row");
                let newVideoCard = createVideoCard(response[0], false, channelId);
                $(`#${channelId}Row`).append(newVideoCard);
                $(`#${videoId}Body`).css("background-color", "#17a2b8");
            }
        }
    });
};
function removeVideoCard(videoId) {
    $(`#${videoId}Div`).remove();
    processingRow = $("#processingVideoRow");
    if (processingRow.children().length == 0 ) {
        let noVideos = $("<p>", {"style": "padding-left: 15px"})
        noVideos.text("No processing videos found.");
        processingRow.append(noVideos);
    }
}
$(document).ready(function () {
    eel.valid_bot()(function (valid) {
        invalid = true;
        while (invalid) {
            if (valid == true) {
                invalid = false;
                eel.get_processing_videos()(function (data) {
                    populateProcessingVideos(data);
                });
                eel.get_user_videos()(function (data) {
                    populateUserVideos(data);
                });
            }
            else {
                eel.init_clip_bot();
                invalid = !eel.valid_bot();
            }
        }
    });
});