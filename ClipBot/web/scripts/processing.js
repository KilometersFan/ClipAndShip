function createVideoCard(data) {
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
    let form = $("<form>", { "id": data["id"] + "Form" })
    let cancelBtn = $("<button>", {
        "class": "btn action-btn", "type": "submit", "value": data["id"], "data-toggle": "modal", "data-target": "#videoMessageModal"
    });
    cancelBtn.text("Cancel Processing");
    form.submit(function (event) {
        event.preventDefault();
        eel.cancelVideo(data["channelId"], data["id"])(function (response) {
            if (response["status"] == 200) {
                col.remove();
            }
            if ($("#videoRow").children().length == 0) {
                let noVideos = $("<p>", { "style": "padding-left: 15px" })
                $("#videoRow").append(noVideos);
            }
        });
    });
    form.append(cancelBtn);
    cardBody.append(h5);
    cardBody.append(p);
    cardBody.append(date);
    cardBody.append(video);
    cardBody.append(form);
    card.append(cardBody);
    col.append(card);
    return col;
}
function populateVideos(data) {
    let row = $("#videoRow");
    row.empty();
    for (let i = 0; i < data.length; i++) {
        let videoCard = createVideoCard(data[i]);
        row.append(videoCard);
    }
    if (data.length == 0) {
        let noVideos = $("<p>", {"style": "padding-left: 15px"})
        noVideos.text("No processing videos found");
        row.append(noVideos);
    }
    $(".loading").hide();
}
$(document).ready(function () {
    eel.validBot()(function (valid) {
        invalid = true;
        while (invalid) {
            if (valid == true) {
                invalid = false;
                eel.getProcessingVideos()(function (data) {
                    populateVideos(data);
                });
            }
            else {
                eel.initClipBot();
                invalid = !eel.validBot();
            }
        }
    });
});