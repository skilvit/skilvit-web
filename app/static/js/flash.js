$("#flash-message").slideDown(function() {
    console.log("Dedans");
    setTimeout(function() {
        $("#flash-message").slideUp();
    }, 5000);
    console.log("On passe dedans ?");
});