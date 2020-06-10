// navigation.html language_picker onchange
$('#language_picker').change(function () {
    var lang = this.value;
    $.ajax({
        url: '/language_change',
        data: lang,
        type: 'POST', // This is needed to post the language_change
        success: function (response) {
            // We don't want to POST the current form on reload (because it could 'submit' the form while it is not the intent of the use)
            // So we prefer to reload the page and lose the data. Therefor the assign.
            // TODO reload without loosing current form
            location.assign(location.href)
            location.reload();
        },
        error: function (error) {
        }
    });
});



