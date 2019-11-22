
jQuery.download = function(url, key, data){
    // Build a form
    var form = $('<form></form>').attr('action', url).attr('method', 'post');
    // Add the one key/value
    form.append($("<input></input>").attr('type', 'hidden').attr('name', key).attr('value', data));
    //send request
    form.appendTo('body').submit().remove();
};


$("#exporter_donnees").on("submit", function () {
    $.download("/tcc/patient/exportation_donnees", "data", "");
    return false;
});
