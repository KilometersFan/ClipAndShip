function createVideoCard(data, processing=true, channelId=null) {
    let col = $("<div>", { "class": "mb-2 mt-2 col-sm-8 col-md-6 col-lg-4", "id": data["id"] + "Div" });
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
    let video = $("<a>", { "class": "card-link", "href": data["url"], "target": "_blank" });
    video.text("Link");
    let container = $("<div>", {"style": "display: block; width: 100%"});
    let btn;
    if (processing) {
        btn = $("<button>", {
            "class": "btn action-btn", "value": data["id"], "data-toggle": "modal", "data-target": "#videoMessageModal"
        });
        btn.text("Cancel Processing");
        btn.click(function() {
            eel.cancelVideo(parseInt(data["channelId"]), parseInt(data["id"]))(function (response) {
                if (response["status"] == 200) {
                    col.remove();
                }
                if ($("#processingVideoRow").children().length == 0) {
                    let noVideos = $("<p>", { "style": "padding-left: 15px" })
                    $("#processingVideoRow").append(noVideos);
                }
                setTimeout(updateVideos, 100);
            });
        });
    }
    else {
        btn = $("<button>", {
            "class": "btn action-btn", "value": data["id"], "data-toggle": "modal", "data-target": "#videoMessageModal"
        });
        btn.text("Clip Video");
        btn.click(async function () {
            eel.clipVideo(parseInt(channelId), parseInt(data["id"]));
        });
    }
    let removeBtn = $("<button>", {
        "class": "btn delete-btn mr-2 ml-2", "type": "button", "value": data["id"], "data-toggle": "modal", "data-target": "#videoRemoveModal"
    });
    removeBtn.text("Remove Video");
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

    cardBody.append(h5);
    cardBody.append(p);
    cardBody.append(date);
    cardBody.append(video);
    if (!processing) {
        let results = $("<a>", { "class": "card-link", "href": "results.html?channel=" + channelId + "&video=" + parseInt(data["id"]), "id": "results" + data["id"] });
        results.text("View Recent Clip");
        cardBody.append(results);
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
            if (videos.length > 0) {
                eel.getVideos(parseInt(channelId), videos)(function (response) {
                    for (let i = 0; i < response.length; i++) {
                        let videoCard = createVideoCard(response[i], false, channelId);
                        row.append(videoCard);
                    }
                });
            }
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