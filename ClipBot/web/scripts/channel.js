let channelId;
let emoteMap;
let twitchEmotes;
let bttvEmotes;
let ffEmotes;
let userCategories = [];
function hasWhiteSpace(s) {
    return /\s/g.test(s);
}
function populateChannelInfo(data) {
    $("#channelImg").attr("src", data["imgUrl"]);
    $("#channelName").text(data["name"]);
    $("#channelDesc").text(data["desc"]);
    channelId = data["id"];
    emoteMap = data["emoteMap"];
    $("#videoBtn").prop("href", "video.html?id=" + channelId);
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
    else if (type === "ffEmotes") {
        emotes = ffEmotes;
        typeUpper = "FF";
    }
    else if (type === "twitchEmotes") {
        emotes = twitchEmotes;
        typeUpper = "Twitch";
        console.log(twitchEmotes);
    }
    for (let i = 0; i < emotes.length; i++) {
        //Create Emote Box from emotes
        let emoteBox = createEmoteBox(emotes[i]["imageUrl"], emotes[i]["name"]);
        row.append(emoteBox);
        let emoteBoxInput = createEmoteBoxInput(emotes[i]["imageUrl"], emotes[i]["name"].toLowerCase(), "emoteBox", "emoteBoxChecked", "Emote", "emotesToAdd");
        formContainer.append(emoteBoxInput);
        for (let j = 0; j < userCategories.length; j++) {
            if (!data[j].emotes.includes(emotes[i]["name"])) {
                let editModalRow = $("#" + userCategories[j] + typeUpper + "EmotesEditModal");
                let editEmoteBoxInput = createEmoteBoxInput(emotes[i]["imageUrl"], emotes[i]["name"].toLowerCase(), "emoteInput", "emoteBoxChecked", "EmoteEdit", "editEmotesToAdd");
                editModalRow.append(editEmoteBoxInput);
            }
        }
    }
    $(".loading").hide();
}
function populateCategoryEmotes(data) {
    console.log(data);
    userCategories = [];
    let rmvSubmit = $("#rmvSubmit");
    $('#rmvCategoryForm div').remove();
    for (let i = 0; i < data.length; i++) {
        let type = data[i]["type"].trim().toLowerCase();
        let div = $("<div>", { "class": "row ml-0 mr-0", "id": type + "Row" });
        div.empty();
        let header = $("<h5>", { "id": type + "Title" });
        header.text(type);
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
        let editCategoryRow = $("<div>", { "class": "row ml-0 mr-0", "id": type + "EditCategoryRow" });

        let editBtn = $("<button>", {
            "type": "button", "id": type + "EditBtn", "class": "btn action-btn mt-1 mb-1 ml-2 mr-2", "data-toggle": "modal", "data-target": "#" + type + "EditModal"
        });
        editBtn.text("Edit");
        editBtn.click(function () {
            editForm.trigger("reset");
        });
        header.append(editBtn);

        let currentTitle = $("<h2>");
        currentTitle.text("Current Emotes");
        editFormGroup.append(currentTitle);
        for (let j = 0; j < data[i]["emotes"].length; j++) {
            // for normal category display
            let name = data[i]["emotes"][j];
            let result;
            let bttvRes = bttvEmotes.find(x => x.name.toLowerCase() === name.toLowerCase());
            let twitchRes = twitchEmotes.find(x => x.name.toLowerCase() === name.toLowerCase());
            let ffRes = ffEmotes.find(x => x.name.toLowerCase() === name.toLowerCase());
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
            let emoteBox = createEmoteBox(result["imageUrl"], emoteMap[name] || name )
            div.append(emoteBox);
            // for modal category display
            let editEmoteBox = createEmoteBoxInput(result["imageUrl"], emoteMap[name] || name, "emoteBoxChecked", "emoteBoxRemove", "EditInput", type + "EmotesToRmv", true);
            editCategoryRow.append(editEmoteBox);
        }
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

        //Create Twitch, FFZ, BTTV emote sections
        let emoteTypes = ["Other", "Twitch", "FF", "BTTV"];
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

        $("#categoriesRow").append(header);
        $("#categoriesRow").append(div);
        $("#categoriesRow").append($("<hr />"))

        editForm.submit(function (event) {
            event.preventDefault();
            emotes_remove = [];
            emotes_add = [];
            emotes_left = [];
            let newValues = [];
            
            [...document.querySelectorAll('input[name="editEmotesToAdd"]:checked')]
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
            eel.editCategory(channelId, type, newValues, emotes_left)(function (response) {
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
    populateEmotes("twitchEmotes", data);
    populateEmotes("ffEmotes", data);
    populateEmotes("bttvEmotes", data);

}
function setEmotes(emotes) {
    twitchEmotes = emotes["twitchEmotes"];
    ffEmotes = emotes["ffEmotes"];
    bttvEmotes = emotes["bttvEmotes"];
    if (bttvEmotes.length == 0) {
        $("#BTTVEmpty").show()
    }
    else {
        $("#BTTVEmpty").hide()
    }
    if (ffEmotes.length == 0) {
        $("#FFEmpty").show()
    }
    else {
        $("#FFEmpty").hide()
    }
    if (twitchEmotes.length == 0) {
        $("#TwitchEmpty").show()
    }
    else {
        $("#TwitchEmpty").hide()
    }
    eel.getCategories(channelId)(populateCategoryEmotes);
}
function populateCategories(id) {
    eel.getChannelEmotes(id)(setEmotes);
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
                    eel.getChannel(id)(populateChannelInfo);
                    populateCategories(id);
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
            eel.addCategory(channelId, type, emotes)(function (response) {
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
            eel.deleteCategory(channelId, categories)(function (response) {
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
    });
    $("#twitchEmotesBtn").click(function () {
        $("#twitchEmotes").slideToggle();
    });
    $("#ffEmotesBtn").click(function () {
        $("#ffEmotes").slideToggle();
    });
    $("#bttvEmotesBtn").click(function () {
        $("#bttvEmotes").slideToggle();
    });
    $("#twitchEmotesModalBtn").click(function () {
        $("#twitchEmotesModal").slideToggle();
    });
    $("#ffEmotesModalBtn").click(function () {
        $("#ffEmotesModal").slideToggle();
    });
    $("#bttvEmotesModalBtn").click(function () {
        $("#bttvEmotesModal").slideToggle();
    });
});