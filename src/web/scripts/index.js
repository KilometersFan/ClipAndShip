$("#credentialForm").submit(function (event) {
    event.preventDefault();
    if (!$("#clientId").val() || !$("#clientSecret").val()) {
        $("#error").show();
    }
    else {
        $("#error").hide();
        eel.enter_credentials($("#clientId").val(), $("#clientSecret").val());
        $("#successBlock").show();
    }
});
function changeDisplay(valid) {
    if (valid === false) {
        $("#invalidBlock").show();
        $("#validBlock").hide();
    }
    else {
        $("#invalidBlock").hide();
        $("#validBlock").show();
    }
}
eel.check_credentials()(changeDisplay);