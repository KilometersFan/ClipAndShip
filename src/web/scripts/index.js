$("#credentialForm").submit(function (event) {
    event.preventDefault();
    if (!$("#clientId").val() || !$("#clientSecret").val()) {
        $("#error").show();
    }
    else {
        $("#error").hide();
        eel.enter_credentials($("#clientId").val(), $("#clientSecret").val());
        $("#successBlock").show();
        $("#credentialForm").hide();s
    }
});
function changeDisplay(response) {
    if (response["status"] === 400) {
        $("#invalidBlock").show();
        $("#validBlock").hide();
        $("#invalidBlock").append(response["msg"]);
    }
    else {
        $("#invalidBlock").hide();
        $("#validBlock").show();
        $("#validBlock").append(response["msg"]);
    }
}
eel.check_credentials()(changeDisplay);