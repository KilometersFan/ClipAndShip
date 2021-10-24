let channelId;
let emoteMap;
let twitchEmotes;
let bttvEmotes;
let ffEmotes;
let _7tvEmotes;
let globalTwitchEmotes;
let globalBTTVEmotes;
let global7TVEmotes;
let userCategories = [];
let globalData;
function hasWhiteSpace(s) {
    return /\s/g.test(s);
}
function populateChannelInfo(data) {
    $("#channelImg").attr("src", data["imgUrl"]);
    $("#channelName").text(data["name"]);
    $("#channelDesc").text(data["desc"]);
    channelId = data["id"];
    emoteMap = data["emoteMap"];
    $("#videoBtn").attr("href", "video.html?id=" + channelId);
}
function createEmoteBox(imageUrl, name) {
    let div = $("<div>", { "class": "col-xs-12 col-sm-auto pt-1 pb-1 pr-1 pl-1 emoteBox" })
    let img = $("<img>", { "src": imageUrl, "alt": name });
    div.append(img);
    let label = $("<p>");
    label.text(name);
    div.append(label);
    return div;
}
function createEmoteBoxInput(imageUrl, name, styleClass, otherStyleClass, idEnd, formName, initChecked=false) {
    let modalDiv = $("<div>", { "class": "col-xs-12 col-sm-auto pt-1 pb-1 pr-1 pl-1 " + styleClass });
    let img = $("<img>", { "src": imageUrl, "alt": name });
    let checkBoxDiv = $("<div>", { "class": "" });
    let input = $("<input>", { "class": "form-check-input invisible", "type": "checkbox", "value": name, "name": formName, "id": name + idEnd + "Label" });
    if (initChecked) {
        input = $("<input>", { "class": "form-check-input invisible", "type": "checkbox", "value": name, "name": formName, "id": name + idEnd + "Label", "checked" : true });
    }
    let checkLabel = $("<label>", { "class": "form-check-label", "for": name + idEnd + "Label" });
    checkLabel.text(name);
    checkBoxDiv.append(checkLabel);
    checkBoxDiv.append(input);
    modalDiv.append(img);
    modalDiv.append(checkBoxDiv);
    modalDiv.click(function (event) {
        let checked = input.prop("checked");
        if (checked && !initChecked) {
            modalDiv.removeClass(otherStyleClass);
            modalDiv.addClass(styleClass);
        }
        else if (checked) {
            modalDiv.addClass(otherStyleClass);
            modalDiv.removeClass(styleClass);
        }
        else if (!checked && !initChecked) {
            modalDiv.removeClass(styleClass);
            modalDiv.addClass(otherStyleClass);
        }
        else if (!checked) {
            modalDiv.removeClass(otherStyleClass);
            modalDiv.addClass(styleClass);
        }
        console.log(`checked: ${checked}, initChecked: ${initChecked}, class: ${modalDiv.attr("class")}`);
        input.prop("checked", !checked);
    });
    return modalDiv;
}
function populateEmotes(type, data) {
    let row = $("#" + type);
    row.empty();
    let formContainer = $("#" + type + "Modal");
    formContainer.empty();
    let emotes;
    let typeUpper = "";
    if (type === "bttvEmotes") {
        emotes = bttvEmotes;
        typeUpper = "BTTV";
    }
    else if (type === "7tvEmotes") {
        emotes = _7tvEmotes;
        typeUpper = "7TV";
    }
    else if (type === "ffEmotes") {
        emotes = ffEmotes;
        typeUpper = "FF";
    }
    else if (type === "twitchEmotes") {
        emotes = twitchEmotes;
        typeUpper = "Twitch";
    }
    else if (type == "globalTwitchEmotes") {
        emotes = globalTwitchEmotes;
        typeUpper = "GlobalTwitch";
    }
    else if (type == "globalBTTVEmotes") {
        emotes = globalBTTVEmotes;
        typeUpper = "GlobalBTTV";
    }
    else if (type == "global7TVEmotes") {
        emotes = global7TVEmotes;
        typeUpper = "Global7TV";
    }
    for (let i = 0; i < emotes.length; i++) {
        //Create Emote Box from emotes
        let emoteBox = createEmoteBox(emotes[i]["imageUrl"], emotes[i]["name"]);
        row.append(emoteBox);
        let emoteBoxInput = createEmoteBoxInput(emotes[i]["imageUrl"], emotes[i]["name"], "emoteBox", "emoteBoxChecked", "Emote", "emotesToAdd");
        formContainer.append(emoteBoxInput);
        for (let j = 0; j < userCategories.length; j++) {
            if (!data[j].emotes.includes(emotes[i]["name"])) {
                let editModalRow = $("#" + userCategories[j] + typeUpper + "EmotesEditModal");
                let editEmoteBoxInput = createEmoteBoxInput(emotes[i]["imageUrl"], emotes[i]["name"], "emoteInput", "emoteBoxChecked", "EmoteEdit", "editEmotesToAdd");
                editModalRow.append(editEmoteBoxInput);
            }
        }
    }
    $(".loading").hide();
}
function updateCategoryEmotes(category) {
    let editCategoryRow = $(`#${category}EditCategoryRow`);
}
function populateCategoryEmotes(data) {
    userCategories = [];
    let rmvSubmit = $("#rmvSubmit");
    $('#rmvCategoryForm div').remove();
    for (let i = 0; i < data.length; i++) {
        let type = data[i]["type"].trim().toLowerCase();
        let div = $("<div>", { "class": "row ml-0 mr-0", "id": type + "Row" });
        div.empty();
        let headerDiv = $("<div>", {"class": "d-flex justify-content-between align-items-center"})
        let header = $("<h5>", { "id": type + "Title", "style": "inline-block" });
        header.text(type);
        headerDiv.append(header);
        userCategories.push(type);

        let rmvDiv = $("<div>", { "class": "form-check", "id": type + "Div" });
        let rmvInput = $("<input>", { "type": "checkbox", "class": "form-check-input", "value": type, "id": type + "Rmv", "name": "categoriesToRmv" });
        let rmvLabel = $("<label>", { "class": "form-check-label", "for": type + "Rmv" });
        rmvLabel.text(type);
        rmvDiv.append(rmvInput);
        rmvDiv.append(rmvLabel);
        rmvSubmit.before(rmvDiv);

        let editModal = $("<div>", { "class": "modal", "id": type + "EditModal", "tabindex": "-1", "role": "dialog", "aria-labelledby": type + "ModalLabel", "aria-hidden": "true" });
        let editDialog = $("<div>", { "class": "modal-dialog modal-lg modal-dialog-centered", "role": "document" });
        let editContent = $("<div>", { "class": "modal-content edit-modal" });
        let editHeader = $("<div>", { "class": "modal-header" });
        let editTitle = $("<h5>", { "class": "modal-title", "id": type + "EditCategoryLabel" });
        editTitle.text("Edit " + type);
        let editBody = $("<div>", { "class": "modal-body" });
        let editContainer = $("<div>", { "class": "container-fluid", "id": type + "EditCategoryContainer" });
        let editForm = $("<form>", { "id": type + "EditForm" });
        let editFormGroup = $("<div>", { "id": type + "EditFormGroup", "class": "form-group" });
        let editCategoryRow = $("<div>", { "class": "d-flex row ml-0 mr-0", "id": type + "EditCategoryRow" });

        let editBtn = $("<button>", {
            "type": "button", "id": type + "EditBtn", "class": "btn action-btn mt-1 mb-1 ml-2 mr-2", "data-toggle": "modal", "data-target": "#" + type + "EditModal"
        });
        editBtn.text("Edit ");
        editBtn.append($("<i>", {"class": "fa fa-edit"}));
        editBtn.click(function () {
            editForm.trigger("reset");
        });
        headerDiv.append(editBtn);

        let currentTitle = $("<h2>");
        currentTitle.text("Current Emotes");
        editFormGroup.append(currentTitle);
        for (let j = 0; j < data[i]["emotes"].length; j++) {
            // for normal category display
            let name = data[i]["emotes"][j];
            let result;
            let bttvRes = bttvEmotes.find(x => x.name.toLowerCase() === name.toLowerCase());
            let _7tvRes = _7tvEmotes.find(x => x.name.toLowerCase() === name.toLowerCase());
            let twitchRes = twitchEmotes.find(x => x.name.toLowerCase() === name.toLowerCase());
            let ffRes = ffEmotes.find(x => x.name.toLowerCase() === name.toLowerCase());
            let globalTwitchRes = globalTwitchEmotes.find(x => x.name.toLowerCase() === name.toLowerCase());
            let globalBTTVRes = globalBTTVEmotes.find(x => x.name.toLowerCase() === name.toLowerCase());
            let globalB7TVRes = global7TVEmotes.find(x => x.name.toLowerCase() === name.toLowerCase());
            if (bttvRes) {
                result = bttvRes;
            }
            else if (_7tvRes) {
                result = _7tvRes;
            }
            else if (twitchRes) {
                result = twitchRes;
            }
            else if (ffRes) {
                result = ffRes;
            }
            else if (globalTwitchRes) {
                result = globalTwitchRes;
            }
            else if (globalBTTVRes) {
                result = globalBTTVRes;
            }
            else if (globalB7TVRes) {
                result = globalB7TVRes;
            }
            else {
                result = { imageUrl: "../error-placeholder.png" };
            }
            let emoteBox = createEmoteBox(result["imageUrl"], emoteMap[name] || name )
            div.append(emoteBox);
            // for modal category display
            console.log(emoteMap[name] || name);
            let editEmoteBox = createEmoteBoxInput(result["imageUrl"], emoteMap[name] || name, "emoteBoxChecked", "emoteBoxRemove", "EditInput", type + "EmotesToRmv", true);
            editCategoryRow.append(editEmoteBox);
        }
        let editFormRecommendedContainer = $("<div>", { "id": "editFormRecommendedContainer", "class": "form-group" });
        let editRecommendedRow = $("<div>", { "class": "d-flex row ml-0 mr-0", "id": type + "EditRecommendedRow" });
        let editFormRecommendedButton = $("<button>", {"class": "btn btn-primary"});
        editFormRecommendedButton.text("Get Recommendations");
        editFormRecommendedButton.click(function (e) {
            e.preventDefault();
            editRecommendedRow.empty();
            eel.get_recommended_emotes(channelId, type)(function (response) {
                if (response.length === 0) {
                    let emptyRecommendations = $("<p>");
                    emptyRecommendations.text("Recommendations are only available after a video is processed.");
                    editRecommendedRow.append(emptyRecommendations);
                }
                for (let i = 0; i < response.length; i++) {
                    let result;
                    let bttvRes = bttvEmotes.find(x => x.name.toLowerCase() === response[i]);
                    let twitchRes = twitchEmotes.find(x => x.name.toLowerCase() === response[i]);
                    let ffRes = ffEmotes.find(x => x.name.toLowerCase() === response[i]);
                    let globalTwitchRes = globalTwitchEmotes.find(x => x.name.toLowerCase() === response[i]);
                    let globalBTTVRes = globalBTTVEmotes.find(x => x.name.toLowerCase() === response[i]);
                    if (bttvRes) {
                        result = bttvRes;
                    }
                    else if (twitchRes) {
                        result = twitchRes;
                    }
                    else if (ffRes) {
                        result = ffRes;
                    }
                    else if (globalTwitchRes) {
                        result = globalTwitchRes;
                    }
                    else if (globalBTTVRes) {
                        result = globalBTTVRes;
                    }
                    else {
                        result = { imageUrl: "../error-placeholder.png" };
                    }
                    let emoteRecommendedBox = createEmoteBoxInput(result["imageUrl"], emoteMap[response[i]] || response[i], "emoteInput", "emoteBoxChecked", "RecommendedEmoteEdit", "editRecommendedEmotesToAdd");
                    editRecommendedRow.append(emoteRecommendedBox);
                }
            });
        });
        editFormRecommendedContainer.append(editFormRecommendedButton);
        editFormRecommendedContainer.append(editRecommendedRow);
        editFormGroup.append(editCategoryRow);
        editForm.append(editFormGroup);
        editContainer.append(editForm);
        editBody.append(editContainer);
        editHeader.append(editTitle);
        editContent.append(editHeader);
        editContent.append(editBody);
        editDialog.append(editContent);
        editModal.append(editDialog);
        div.append(editModal);

        let emoteAddTitle = $("<h2>", { "class": "mt-2 mb-2" });
        emoteAddTitle.text("Emotes to Add");
        editFormGroup.append(emoteAddTitle);
        editFormGroup.append(editFormRecommendedContainer);
        //Create Twitch, FFZ, BTTV emote sections
        let emoteTypes = ["Other", "Twitch", "FF", "BTTV", "7TV", "GlobalTwitch", "GlobalBTTV", "Global7TV"];
        emoteTypes.forEach((emoteType) => {
            let emoteTitle = $("<h3>", { "class": "mt-2 mb-2" });
            emoteTitle.text(emoteType + " Emotes");
            editFormGroup.append(emoteTitle);
            let emotesEditModalDiv = $("<div>", { "class": "row ml-0 mr-0", "id": type + emoteType + "EmotesEditModal" });
            if (emoteType == "Other") {
                let otherEmotesInput = $("<input>", { "type": "text", "id": type + "OtherEmotesInput", "name": type + "OtherEmotesInput", "placeholder": "Kappa, LUL, PogChamp", "class": "form-control" });
                emotesEditModalDiv.append(otherEmotesInput);
                let subtitle = $("<p>");
                subtitle.text("Add global twitch emotes, or other 1 word phrases, in a comma separated list. Text with spaces will not be added.");
                editFormGroup.append(subtitle);
            }
            else {
                let emotesEditModalBtn = $("<button>", { "type": "button", "id": type + emoteType + "EmotesEditModalBtn", "class": "btn toggle-btn mt-1 mb-1" });
                emotesEditModalBtn.text("Toggle View");
                emotesEditModalBtn.click(function () {
                    emotesEditModalDiv.slideToggle();
                });
                editFormGroup.append(emotesEditModalBtn);
            }
            editFormGroup.append(emotesEditModalDiv);
        });

        let editSubmit = $("<button>", { "type": "submit", "id": type + "EditSubmit", "class": "btn action-btn mt-1 mb-1" });
        editSubmit.text("Save Changes");
        editForm.append(editSubmit);
        $("#categoriesRow").append($("<hr>", {"style": "background-color: white; margin-top: .5rem; margin-bottom: .5rem"}));
        $("#categoriesRow").append(headerDiv);
        $("#categoriesRow").append($("<hr>", {"style": "background-color: white; margin-top: .5rem; margin-bottom: .5rem"}));
        $("#categoriesRow").append(div);

        editForm.submit(function (event) {
            event.preventDefault();
            emotes_remove = [];
            emotes_add = [];
            emotes_left = [];
            let newValues = [];
            
            [...document.querySelectorAll('input[name="editEmotesToAdd"]:checked')]
                .forEach((cb) => emotes_add.push(cb));
            [...document.querySelectorAll('input[name="editRecommendedEmotesToAdd"]:checked')]
                .forEach((cb) => emotes_add.push(cb));
            [...document.querySelectorAll('input[name="' + type + 'EmotesToRmv"]:checked')]
                .forEach((cb) => emotes_left.push(cb.value.toLowerCase()));
            [...document.querySelectorAll('input[name="' + type + 'EmotesToRmv"]:not(:checked)')]
                .forEach((cb) => emotes_remove.push(cb.value.toLowerCase()));

            let otherEmotes = $("#" + type + "OtherEmotesInput").val().trim();
            if (otherEmotes) {
                otherEmotes = otherEmotes.split(",");
                for (let m = 0; m < otherEmotes.length; m++) {
                    otherEmotes[m] = otherEmotes[m].trim().toLowerCase();
                }
            }
            emotes_add.forEach((cb) => newValues.push(cb.value.toLowerCase()));
            for (let m = 0; m < otherEmotes.length; m++) {
                if (!hasWhiteSpace(otherEmotes[m])) {
                    newValues.push(otherEmotes[m]);
                }
            }
            eel.edit_category(channelId, type, newValues, emotes_left)(function (response) {
                console.log(response);
                if (!response) {
                    editModal.modal("hide");
                    $("#categoriesRow").empty();
                    populateCategories(channelId);
                    $("#categoryLoading").show();
                }
                else {
                    $(".error").text("Unable to add category: " + response);
                    $(".error").show();
                }
            });
        });
    }
    $("#categoryLoading").hide();
    globalData = data;
    populateEmotes("twitchEmotes", globalData);
    populateEmotes("ffEmotes", globalData);
    populateEmotes("bttvEmotes", globalData);
    populateEmotes("7tvEmotes", globalData);
    populateEmotes("globalTwitchEmotes", globalData);
    populateEmotes("globalBTTVEmotes", globalData);
    populateEmotes("global7TVEmotes", globalData);
}
function setEmotes(channel_emotes) {
    twitchEmotes = channel_emotes["twitchEmotes"];
    ffEmotes = channel_emotes["ffEmotes"];
    bttvEmotes = channel_emotes["bttvEmotes"];
    _7tvEmotes = channel_emotes["7tvEmotes"]
    if (bttvEmotes.length == 0) {
        $("#BTTVEmpty").show();
    }
    else {
        $("#BTTVEmpty").hide();
    }
    if (_7tvEmotes.length == 0) {
        $("#7TVEmpty").show()
    }
    else {
        $("#7TVEmpty").hide()
    }
    if (ffEmotes.length == 0) {
        $("#FFEmpty").show();
    }
    else {
        $("#FFEmpty").hide();
    }
    if (twitchEmotes.length == 0) {
        $("#TwitchEmpty").show();
    }
    else {
        $("#TwitchEmpty").hide();
    }
    if (globalTwitchEmotes.length == 0) {
        $("#globalTwitchEmpty").show();
    }
    else {
        $("#globalTwitchEmpty").hide();
    }
    if (globalBTTVEmotes.length == 0) {
        $("#globalBTTVEmpty").show();
    }
    else {
        $("#globalBTTVEmpty").hide();
    }
    if (global7TVEmotes.length == 0) {
        $("#global7TVEmpty").show();
    }
    else {
        $("#global7TVEmpty").hide();
    }
    eel.get_categories(channelId)(populateCategoryEmotes);
}
function populateCategories(id) {
    eel.get_channel_emotes(id)(function (channel_emotes) {
        eel.get_twitch_global_emotes()(function (twitch_global_emotes) {
            globalTwitchEmotes = twitch_global_emotes["emotes"];
            eel.get_bttv_global_emotes()(function (bttv_global_emotes) {
                globalBTTVEmotes = bttv_global_emotes["emotes"];
                eel.get_bttv_global_emotes()(function (_7tv_global_emotes) {
                    global7TVEmotes = _7tv_global_emotes["emotes"];
                    console.log(twitch_global_emotes["emoteMap"]);
                    console.log(bttv_global_emotes["emoteMap"]);
                    console.log(_7tv_global_emotes["emotesMap"]);
                    emoteMap = {
                        ...emoteMap,
                        ...twitch_global_emotes["emoteMap"],
                        ...bttv_global_emotes["emoteMap"],
                        ..._7tv_global_emotes["emoteMap"],
                    }
                    setEmotes(channel_emotes);
                });
            });
        });
    });
}
$(document).ready(function () {
    eel.valid_bot()(function (valid) {
        invalid = true;
        while (invalid) {
            if (valid == true) {
                invalid = false;
                let searchParams = new URLSearchParams(window.location.search);
                if (searchParams.has("id") && searchParams.get("id")) {
                    let id = parseInt(searchParams.get("id"));
                    eel.get_channel(id)(populateChannelInfo);
                    populateCategories(id);
                }
                else {
                    $("#numChannels").html("No channels found.")
                }
            }
            else {
                eel.init_clip_bot();
                invalid = !eel.valid_bot();
            }
        }
    });
    $("#recommendedBtn").click(function (e) {
        e.preventDefault();
        $("#recommendedRow").empty();
        let emotes = [];
        [...document.querySelectorAll('input[name="emotesToAdd"]:checked')]
                .forEach((cb) => emotes.push(cb.value));
        let emptyRecommendations = $("<p>");
        if (emotes.length === 0) {
            emptyRecommendations.text("Please choose at least one emote to calculate recommendations.");
            $("#categoryRecommendedContainer").append(emptyRecommendations)
        }
        else {
            eel.get_recommended_emotes(channelId, emotes, true)(function (response) {
                if (response.length === 0) {
                    emptyRecommendations.text("Recommendations are only available after a video is processed.");
                    $("#categoryRecommendedContainer").append(emptyRecommendations)
                }
                for (let i = 0; i < response.length; i++) {
                    let result;
                    let bttvRes = bttvEmotes.find(x => x.name.toLowerCase() === response[i]);
                    let twitchRes = twitchEmotes.find(x => x.name.toLowerCase() === response[i]);
                    let ffRes = ffEmotes.find(x => x.name.toLowerCase() === response[i]);
                    if (bttvRes) {
                        result = bttvRes;
                    }
                    else if (twitchRes) {
                        result = twitchRes;
                    }
                    else if (ffRes) {
                        result = ffRes;
                    }
                    else {
                        result = { imageUrl: "../error-placeholder.png" };
                    }
                    let emoteRecommendedBox = createEmoteBoxInput(result["imageUrl"], emoteMap[response[i]] || response[i], "emoteInput", "emoteBoxChecked", "RecommendedEmoteEdit", "recommendedEmotesToAdd");
                    $("#recommendedRow").append(emoteRecommendedBox);
                }
            });
        }
    });
    $("#categoryForm").submit(function (event) {
        event.preventDefault()
        if (!$("#newCategory").val()) {
            $(".error").text("Please fill out all required fields.");
            $(".error").show();
        }
        else if (hasWhiteSpace($("#newCategory").val())) {
            $(".error").text("Whitespace characters are not allowed for category names.");
            $(".error").show();
        }
        else {
            $(".error").hide();
            let emotes = [];
            let type = $("#newCategory").val();
            console.log(document.querySelectorAll('input[name="emotesToAdd"]:checked'));
            [...document.querySelectorAll('input[name="emotesToAdd"]:checked')]
                .forEach((cb) => emotes.push(cb.value));
            [...document.querySelectorAll('input[name="recommendedEmotesToAdd"]:checked')]
                .forEach((cb) => emotes.push(cb.value));
            let otherEmotes = $("#addOtherEmotes").val();
            if (otherEmotes) {
                otherEmotes = otherEmotes.split(",");
                console.log(otherEmotes);
                for (let m = 0; m < otherEmotes.length; m++) {
                    otherEmotes[m] = otherEmotes[m].trim();
                }
                for (let m = 0; m < otherEmotes.length; m++) {
                    if (!hasWhiteSpace(otherEmotes[m])) {
                        emotes.push(otherEmotes[m]);
                    }
                }
            }
            console.log(otherEmotes);
            console.log(`{type}: `);
            console.log(emotes);
            eel.add_category(channelId, type, emotes)(function (response) {
                if (!response) {
                    $('#addCategoryModal').modal('hide');
                    $("#categoriesRow").empty();
                    populateCategories(channelId);
                    $("#categoryLoading").show();
                }
                else {
                    $(".error").text("Unable to add category: " + response);
                    $(".error").show();
                }
            });
        }
    });
    $("#addCategoryBtn").click(function () {
        populateEmotes("twitchEmotes", globalData);
        populateEmotes("ffEmotes", globalData);
        populateEmotes("bttvEmotes", globalData);
        populateEmotes("7tvEmotes", globalData);
        populateEmotes("globalBTTVEmotes", globalData);
        populateEmotes("globalTwitchEmotes", globalData);
        populateEmotes("global7TVEmotes", globalData);
        $("#categoryForm").trigger("reset");
        $(".error").hide();
    });
    $("#rmvCategoryForm").submit(function (event) {
        event.preventDefault();
        let categories = [];
        [...document.querySelectorAll('input[name="categoriesToRmv"]:checked')]
            .forEach((cb) => categories.push(cb.value));
        if (categories.length == 0) {
            $(".error").text("Please choose at least one category.");
            $(".error").show();
        }
        else {
            $(".error").hide();
            eel.delete_category(channelId, categories)(function (response) {
                if (!response) {
                    $('#rmvCategoryModal').modal('hide');
                    $("#categoriesRow").empty();
                    populateCategories(channelId);
                    $("#categoryLoading").show();
                }
                else {
                    $(".error").text("Unable to remove category: " + response);
                    $(".error").show();
                }

            })
        }
    });
    $("#rmvCategoryBtn").click(function () {
        $("#rmvCategoryForm").trigger("reset");
        $(".error").hide();
    });
    $("#categoriesBtn").click(function () {
        $("#categories").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).children('i').eq(0).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });
    $("#twitchEmotesBtn").click(function () {
        $("#twitchEmotes").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).children('i').eq(0).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });
    $("#ffEmotesBtn").click(function () {
        $("#ffEmotes").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).children('i').eq(0).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });
    $("#bttvEmotesBtn").click(function () {
        $("#bttvEmotes").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).children('i').eq(0).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });
    $("#7tvEmotesBtn").click(function () {
        $("#7tvEmotes").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).children('i').eq(0).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });
    $("#globalTwitchEmotesBtn").click(function () {
        $("#globalTwitchEmotes").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).children('i').eq(0).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });
    $("#globalBTTVEmotesBtn").click(function () {
        $("#globalBTTVEmotes").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).children('i').eq(0).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });
    $("#global7TTVEmotesBtn").click(function () {
        $("#global7TVEmotes").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).children('i').eq(0).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });
    $("#twitchEmotesModalBtn").click(function () {
        $("#twitchEmotesModal").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).children('i').eq(0).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });
    $("#ffEmotesModalBtn").click(function () {
        $("#ffEmotesModal").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).children('i').eq(0).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });
    $("#bttvEmotesModalBtn").click(function () {
        $("#bttvEmotesModal").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });

    $("#7tvEmotesModalBtn").click(function () {
        $("#7tvEmotesModal").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });

    $("#globalTwitchEmotesModalBtn").click(function () {
        $("#globalTwitchEmotesModal").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).children('i').eq(0).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });
    $("#globalBTTVEmotesModalBtn").click(function () {
        $("#globalBTTVEmotesModal").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).children('i').eq(0).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });

    $("#global7TVEmotesModalBtn").click(function () {
        $("#global7TVEmotesModal").slideToggle();
        if ($(this).children('i').eq(0).hasClass("fa-toggle-on")) {
            $(this).children('i').eq(0).removeClass("fa-toggle-on");
            $(this).children('i').eq(0).addClass("fa-toggle-off");
        }
        else {
            $(this).children('i').eq(0).removeClass("fa-toggle-off");
            $(this).children('i').eq(0).addClass("fa-toggle-on");
        }
    });
});