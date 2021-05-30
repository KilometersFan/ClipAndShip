let channelId;
let channel_name;
function populateVideos() {
    let row = $("#videoRow");
    row.empty();
    eel.getVideos(channelId)(function (data) {
        for (let i = 0; i < data.length; i++) {
            let videoCard = createVideoCard(data[i], false, false, true);
            row.append(videoCard);
        }
        $(".loading").hide();
    });
}
function populateUserVideos(channel_name) {
    $("#userVideos").empty();
    eel.getUserVideos(channel_name)(function (videos) {
        if (!videos.length) {
            let noVideos = $("<p>", { "style": "padding-left: 15px" });
            noVideos.text("No clipped videos found.");
            $("#userVideos").append(noVideos);
        }
        else {
            eel.getVideos(channelId, videos)(function (data) {
                let row = $("#userVideos");
                for (let i = 0; i < data.length; i++) {
                    let videoCard = createVideoCard(data[i], false, true, true);
                    row.append(videoCard);
                }
                $(".loading").hide();
            });
        }
    });
}
function updateVideos() {
    populateVideos();
    populateUserVideos(channel_name);
}
function createVideoCard(data, search = false, remove = false, results = false) {
    let col = $("<div>", { "class": "mb-2 mt-2", "id": data["id"] + "Div" });
    if (search) {
        col.addClass("col-sm-12");
    }
    else {
        col.addClass("col-sm-8 col-md-6 col-lg-4");
    }
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
    let form = $("<form>", { "id": data["id"] + "Form" })
    let processing = data["processing"];
    let clipBtn;
    if (processing) {
        clipBtn = $("<button>", {
            "class": "btn action-btn", "type": "submit", "value": data["id"], "data-toggle": "modal", "data-target": "#videoCancelModal"
        });
    }
    else {
        clipBtn = $("<button>", {
            "class": "btn action-btn", "type": "submit", "value": data["id"], "data-toggle": "modal", "data-target": "#videoMessageModal"
        });
    }
    if (processing) {
        clipBtn.text("Cancel Processing");
    }
    else {
        clipBtn.text("Clip Video");
    }
    if (search) {
        clipBtn.click(function () {
            $("#searchModal").modal('hide');
        });
    }
    form.submit(function (event) {
        event.preventDefault();
        let id = data["id"];
        if (processing) {
            eel.cancelVideo(data["channelId"], data["id"])(function (response) {
                if (response["status"] == 201) {
                    $("#cancelResponse").text(response["msg"]);
                }
                else {
                    $("#cancelResponse").text("An error occurred when cancelling the video.");
                }
            });
            setTimeout(updateVideos, 100);
        }
        else {
            eel.clipVideo(channelId, id);
            setTimeout(updateVideos, 100);
        }
    });
    form.append(clipBtn);
    if (remove) {
        let removeBtn = $("<button>", {
            "class": "btn delete-btn mr-2 ml-2", "type": "button", "value": data["id"], "data-toggle": "modal", "data-target": "#videoRemoveModal"
        });
        removeBtn.text("Remove Video");
        removeBtn.click(function () {
            let videoToRmv = removeBtn.val();
            eel.removeVideo(channel_name, videoToRmv)(function (response) {
                if (response.success) {
                    $("#rmvBody").text("Successfully removed video from your list.")
                }
                else {
                    $("#rmvBody").text("Unable to remove video from your list.")
                }
                populateVideos();
                populateUserVideos(channel_name);
            });
        });
        form.append(removeBtn);
    }
    cardBody.append(h5);
    cardBody.append(p);
    cardBody.append(date);
    cardBody.append(video);
    if (results) {
        let results = $("<a>", { "class": "card-link", "href": "results.html?channel=" + channelId + "&video=" + data["id"], "id": "results" + data["id"] });
        results.text("View Recent Clip");
        cardBody.append(results);
        if (data["clipped"] === true) {
            results.show();
        }
        else {
            results.hide();
        }
    }
    cardBody.append(form);
    card.append(cardBody);
    col.append(card);
    return col;
}
$(document).ready(function () {
    eel.validBot()(function (valid) {
        invalid = true;
        while (invalid) {
            if (valid == true) {
                invalid = false;
                let searchParams = new URLSearchParams(window.location.search);
                if (searchParams.has("id") && searchParams.get("id")) {
                    let id = parseInt(searchParams.get("id"));
                    channelId = id;
                    $("#channelBtn").prop("href", "channel.html?id=" + channelId);
                    eel.getChannel(id)(function (data) {
                        $("#channelVideoTitle").text(data["name"] + "'s Videos");
                        channel_name = data["name"];
                        populateVideos();
                        populateUserVideos(data["name"]);
                    });
                }
                else {
                    $("#numChannels").html("No channels found.")
                }
            }
            else {
                eel.initClipBot();
                invalid = !eel.validBot();
            }
        }
    });
    $("#channelVideoBtn").click(function () {
        $("#videoRow").slideToggle();
    });
    $("#userVideosBtn").click(function () {
        $("#userVideos").slideToggle();
    });
    $("#searchVideoBtn").click(function () {
        $("#searchVideoForm").trigger("reset");
        $("#videoSearchResult").empty();
    });
    $("#searchVideoForm").submit(function (event) {
        event.preventDefault();
        $("#videoSearchResult").empty();
        let video = $("#searchInput").val();
        video = video.trim();
        video = parseInt(video);
        if (!video) {
            $(".error").text("Please enter a video id.");
            $(".error").show();
        }
        else {
            $(".error").hide();
            eel.getVideos(channelId, [video])(function (data) {
                if (data.error) {
                    $("#searchNotFound").show();
                    $("#searchNotFound").text(data.error);
                }
                else {
                    $("#searchNotFound").hide();
                    let result = $("#videoSearchResult");
                    let videoCard = createVideoCard(data[0], true, false, false)
                    result.append(videoCard);
                }
            });
        }
    });
});