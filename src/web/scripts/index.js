$("#credentialForm").submit(function (event) {
    event.preventDefault();
    if (!$("#clientId").val() || !$("#clientSecret").val()) {
        $("#error").show();
    }
    else {
        $("#error").hide();
        eel.enter_credentials($("#clientId").val(), $("#clientSecret").val())(function (response) {
            $("#successBlock").append(response);
        });
        $("#successBlock").show();
        eel.check_credentials()(changeDisplay);
    }
});
function changeDisplay(response) {
    if (response["success"] === false) {
        console.log(response["msg"]);
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