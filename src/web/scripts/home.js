let channels;
function createChannelCard(channelName, channelId, channelDesc, channelImg, search=false) {
    let col = $("<div>", { "class": "mb-2 mt-2 d-flex align-self-stretch", "id": channelId + "Div" });
    if (search) {
        col.addClass("col-sm-12 pl-0 pr-0 d-flex align-self-stretch");
    }
    else {
        col.addClass("col-sm-8 col-md-6 col-lg-4");
    }
    let card = $("<div>", { "class": "card custom-card" });
    let img = $("<img>", { "class": " card-img-top", "src": channelImg, "alt": channelName })
    card.append(img)
    let cardBody = $("<div>", { "class": "card-body" });
    let h5 = $("<h5>", { "class": "card-title" });
    h5.text(channelName);
    let p = $("<p>", { "class": "card-text" });
    p.text(channelDesc);
    let settings;
    let video;
    if (!search) {
        settings = $("<a>", { "class": "card-link", "href": "channel.html?id=" + channelId });
        settings.text("Edit Settings");
        video = $("<a>", { "class": "card-link", "href": "video.html?id=" + channelId });
        video.text("Process Video");
    }
    cardBody.append(h5);
    cardBody.append(p);
    if (!search) {
        cardBody.append(settings);
        cardBody.append(video);
    }
    card.append(cardBody);
    col.append(card);
    return col;
}
function setChannels(c) {
    channels = c;
    sessionStorage.setItem("channels", JSON.stringify(channels));
    $("#channelsContainer").empty();
    for (let i = 0; i < channels.length; i++) {
        // Add channel cards
        let cardCol = createChannelCard(channels[i]["name"], channels[i]["id"], channels[i]["desc"], channels[i]["imgUrl"]);
        $("#channelsContainer").append(cardCol);

        // Add channels to remove form
        let formGroup = $("<div>", { "class": "form-check", "id": channels[i][1] + "RmvDiv" });
        let rmvInput = $("<input>", { "type": "checkbox", "class": "form-check-input", "value": channels[i]["id"], "id": channels[i]["id"] + "Rmv", "name": "channelsToRmv" });
        let rmvLabel = $("<label>", { "class": "form-check-label", "for": channels[i]["name"] + "Rmv" });
        rmvLabel.text(channels[i]["name"]);
        formGroup.append(rmvInput);
        formGroup.append(rmvLabel);
        $("#rmvChannelSubmit").before(formGroup);
    }
    $("#loading").hide();
}

$(document).ready(function () {
    eel.initClipBot();
    eel.validBot()(function (valid) {
        if (valid == true) {
            eel.getChannels()(setChannels);
        }
        else {
            $("#numChannels").html("No channels found.")
        }
    });
    $("#searchChannelBtn").click(function () {
        $("#searchInput").prop("disabled", false);
        $("#searchChannelForm").trigger("reset");
        $("#addChannelForm").trigger("reset");
        $("#searchChannelResult").empty();
        $("#addChannelForm").hide();
        $(".errorChannel").hide();
        $(".errorChannel").text("");
    })
    $("#searchChannelForm").submit(function (event) {
        event.preventDefault();
        let channel = $("#searchInput").val();
        if (!channel) {
            $(".error").text("Please enter a channel name.");
            $(".error").show();
        }
        else {
            $("#searchInput").prop("disabled", true);
            $(".error").hide();
            eel.searchChannel(channel)(function (result) {
                $("#searchChannelResult").empty();
                if (result != null) {
                    $("#notFound").hide();
                    $("#addChannelForm").show();
                    let cardCol = createChannelCard(result.displayName, result.id, result.desc, result.imgURL, true)
                    $("#searchChannelResult").append(cardCol);
                    $("#addChannelSubmit").val(result.id);
                }
                else {
                    $("#notFound").show();
                    $("#addChannelForm").hide();
                }
            });
        }

    });
    $("#clearChannelSubmit").click(function () {
        $("#searchChannelResult").empty();
        $("#searchInput").prop("disabled", false);
        $("#searchInput").val("");
        $("#addChannelForm").hide();
    })
    $("#addChannelForm").submit(function (event) {
        event.preventDefault();
        let channel = $("#addChannelSubmit").val()
        if (channel) {
            eel.addChannel(channel)(function (response) {
                if (response) {
                    $(".errorChannel").show();
                    $(".errorChannel").text(response[0]);
                }
                else {
                    let name = $("#searchInput").val();
                    $(".errorChannel").hide();
                    $(".errorChannel").text("");
                    eel.searchChannel(name)(function (result) {
                        // Add channel card
                        let searchCard = createChannelCard(result.displayName, result.id, result.desc, result.imgURL);
                        $("#channelsContainer").append(searchCard);
                        $("#addChannelModal").modal("hide");

                        // Add channels to remove form
                        let formGroup = $("<div>", { "class": "form-check", "id": result.id + "RmvDiv" });
                        let rmvInput = $("<input>", { "type": "checkbox", "class": "form-check-input", "value": result.id, "id": result.displayName + "Rmv", "name": "channelsToRmv" });
                        let rmvLabel = $("<label>", { "class": "form-check-label", "for": result.displayName + "Rmv" });
                        rmvLabel.text(result.displayName);
                        formGroup.append(rmvInput);
                        formGroup.append(rmvLabel);
                        $("#rmvChannelSubmit").before(formGroup);
                    });

                }
            });
        }
    });
    $("#rmvChannelForm").submit(function (event) {
        event.preventDefault();
        let channelsRmv = [];
        [...document.querySelectorAll('input[name="channelsToRmv"]:checked')]
            .forEach((cb) => channelsRmv.push(cb.value));
        if (channelsRmv.length == 0) {
            $(".error").text("Please choose at least one channel.");
            $(".error").show();
        }
        else {
            $(".error").hide();
            eel.removeChannels(channelsRmv)(function (response) {
                if (!response) {
                    $('#rmvChannelModal').modal('hide');
                    $("#rmvChannelForm div").remove();
                    eel.getChannels()(setChannels);
                }
                else {
                    $(".error").text("Unable to remove channel: " + response);
                    $(".error").show();
                }
            });
        }
    });
});