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
    let container = $("<div>", { "class": "d-flex justify-content-between", "style": "display: block; width: 100%" });
    let btn;
    if (!processing) {
        btn = $("<button>", {
            "class": "btn action-btn mx-0", "value": data["id"], "data-toggle": "modal", "data-target": "#videoMessageModal"
        });
        btn.text("Process");
        btn.click(async function () {
            eel.clipVideo(parseInt(channelId), parseInt(data["id"]));
            setTimeout(updateVideos, 200);
        });
        let removeBtn = $("<button>", {
            "class": "btn delete-btn mr-1", "type": "button", "value": data["id"], "data-toggle": "modal", "data-target": "#videoRemoveModal"
        });
        removeBtn.text("Remove");
        removeBtn.click(function () {
            let videoToRmv = removeBtn.val();
            eel.removeVideo(channelId, videoToRmv)(function (response) {
                if (response.success) {
                    $("#rmvBody").text("Successfully removed video from your list.")
                }
                else {
                    $("#rmvBody").text("Unable to remove video from your list.")
                }
                eel.getUserVideos()(function (data) {
                    populateUserVideos(data);
                });
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
    row.empty();
    if (Object.keys(data).length == 0) {
        let noVideos = $("<p>", {"style": "padding-left: 15px"})
        noVideos.text("No user videos found.");
        row.append(noVideos);
    }
    else {
        Object.keys(data).forEach((channelId) => {
            let videos = data[channelId];
            eel.getChannel(parseInt(channelId))(function (data) {
                let channelCol = $("<div>", {"class": "col-sm-12"});
                let channelRow = $("<div>", {"class": "row"});
                let channelContainer = $("<div>", {"class": "col-sm-12 d-flex align-items-center"});
                let channelName = $("<h3>", {"class": "p-2 mr-auto"});
                channelName.text(data["name"]);
                channelContainer.append(channelName);
                let channelVideos = $("<a>", {"class": "btn btn-primary p-2", "href": "video.html?id=" + channelId});
                channelVideos.text("Channel Videos");
                let channelSettings = $("<a>", {"class": "btn btn-secondary p-2 mr-2", "href": "channel.html?id=" + channelId});
                channelSettings.text("Channel Settings");
                channelContainer.append(channelSettings);
                channelContainer.append(channelVideos);
                channelRow.append(channelContainer);
                if (videos.length > 0) {
                    eel.getVideos(parseInt(channelId), videos)(function (response) {
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
    }
    $(".loading").hide();
}

function updateVideos() {
    eel.getProcessingVideos()(function (data) {
        populateProcessingVideos(data);
    });
    eel.getUserVideos()(function (data) {
        populateUserVideos(data);
    });
}

$(document).ready(function () {
    eel.validBot()(function (valid) {
        invalid = true;
        while (invalid) {
            if (valid == true) {
                invalid = false;
                eel.getProcessingVideos()(function (data) {
                    populateProcessingVideos(data);
                });
                eel.getUserVideos()(function (data) {
                    populateUserVideos(data);
                });
            }
            else {
                eel.initClipBot();
                invalid = !eel.validBot();
            }
        }
    });
});