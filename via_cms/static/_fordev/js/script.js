function saveUserActive(id, active, functionUrl) {
    var data = {"user_id": id, "active": active};
    $.ajax({
        async: true,
        type: "POST",
        url: functionUrl,
        data: JSON.stringify(data, null, 3),
        contentType: "application/json",
        success: function (response) {
            if (response.status != 'ok') {
                $('#ajax-error').html('<div class="col-md-12"><div class="alert alert-warning"><a class="close" title="Close" href="#" data-dismiss="alert">×</a>' + response.replace(/\n/g, "<br/>") + '</div></div></div>');
            } else {
                update_user_dashboard_table(id, response.active);
            }
        },
        error: function (error) {
            $('#error').html(error);
        }
    });
}

function saveUserPassword(id, new_pass, functionUrl) {
    var data = {"user_id": id, "new_pass": new_pass};
    $.ajax({
        async: true,
        type: "POST",
        url: functionUrl,
        data: JSON.stringify(data, null, 3),
        contentType: "application/json",
        success: function (response) {
            if (response.status != 'ok') {
                $('#ajax-error').html('<div class="col-md-12"><div class="alert alert-warning"><a class="close" title="Close" href="#" data-dismiss="alert">×</a>' + response.replace(/\n/g, "<br/>") + '</div></div></div>');
            } else {
                alert('Password changed successfully!');
                $('#passModal').modal('hide')
            }
        },
        error: function (error) {
            $('#error').html(error);
        }
    });
}


function update_user_dashboard_table(id, active) {
    var user_row = document.getElementById('user-' + id)
    var user_action_active = document.getElementById('user-action-active-' + id)
    var user_active = document.getElementById('user-active-' + id)
    if (active) {
        is_active = "Yes";
        title = "Disable";
        active_color = "green";
        not_active_color = "red";
        active_icon = "fa-times-circle";
    } else {
        is_active = "No";
        title = "Enable";
        active_color = "red";
        not_active_color = "green";
        active_icon = "fa-check-circle";
    }
    user_active.innerHTML = is_active;
    user_active.style.color = active_color;
    user_action_active.setAttribute("data-content", active);
    user_action_active.setAttribute("title", title);
    user_action_active.style.color = not_active_color;
    user_action_active.innerHTML = '<i class="far ' + active_icon + '"></i>';
}

function addContactField() {
    var contact_row = document.getElementById('contact-row');
    var contact_field = document.createElement("textarea");
    var contact_type_field = document.createElement("textarea");

    contact_type_field.classList.add("form-control", "contact-type-field", "col-2");
    contact_type_field.setAttribute("rows", "1");
    contact_type_field.setAttribute("placeholder", "Email");

    contact_field.classList.add("form-control", "contact-field", "col-10");
    contact_field.setAttribute("rows", "1");
    contact_field.setAttribute("placeholder", "name@example.com");

    contact_row.appendChild(contact_type_field);
    contact_row.appendChild(contact_field);
}

function str2Json(str) {
    return str.replace(/[\\]/g, '\\\\')
        .replace(/[\"]/g, '\\\"')
        .replace(/[\/]/g, '\\/')
        .replace(/[\b]/g, '\\b')
        .replace(/[\f]/g, '\\f')
        .replace(/[\n]/g, '\\n')
        .replace(/[\r]/g, '\\r')
        .replace(/[\t]/g, '\\t');
};

function getJson() {
    var contact_lst = document.getElementsByClassName('contact-field');
    var contact_type_lst = document.getElementsByClassName('contact-type-field');
    var contact_json_str = ""; // TODO temporary until there is proper mechanism implemented for contacts

    if (contact_lst.length > 0 && contact_lst.item(0).value != '' && contact_type_lst.item(0).value != "") {
        for (var i = 0; i < contact_lst.length; i++) {
            if ((contact_lst.item(i).value != "") && (contact_type_lst.item(i).value != "")) {
                if (i > 0) {
                    contact_json_str += ",";
                }
                contact_json_str += "\"" + str2Json(contact_type_lst.item(i).value) + "\":";
                contact_json_str += "\"" + str2Json(contact_lst.item(i).value) + "\"";
            }
        }
    }

    var body_json_element_list = document.getElementsByClassName('for-body');
    var body_json_builder = '';
    // TODO add better check
    if (body_json_element_list.length > 0 && body_json_element_list.item(0).id != "") {
        body_json_builder = "{";
        for (var i = 0; i < body_json_element_list.length; i++) {
            if (body_json_element_list.item(i).value && body_json_element_list.item(i).value != "") {
                if (body_json_element_list.item(i).id == 'end_date') {
                    if (body_json_element_list.item(i).value != "") {
                        // remove the previous double quote (which is escaped)
                        body_json_builder = body_json_builder.substr(0, body_json_builder.length - 1);
                        // add the end date
                        body_json_builder += " - " + str2Json(body_json_element_list.item(i).value) + "\""
                    }
                } else {
                    if (i > 0) {
                        body_json_builder += ",";
                    }
                    body_json_builder += "\"" + str2Json(body_json_element_list.item(i).dataset['label']) + "\":";
                    body_json_builder += "\"" + str2Json(body_json_element_list.item(i).value) + "\"";
                }
            }
        }
        // end for
        // if (contact_json_str.length > 0) {
        //     if(body_json_builder != "") {
        //         body_json_builder += ",";
        //     }
        //     body_json_builder += "\"" + document.getElementById('contact-label').textContent + "\":{"
        //         + contact_json_str + "}";
        // }
        body_json_builder += "}";
    }

// TODO temporary until there is proper mechanism implemented for contacts
    contact_json_str = "{" + contact_json_str + "}";

    var body_json = document.getElementById('body_json');
    var contact_json = document.getElementById('contact_json');
    var feedback_definition = document.getElementById('feedback_definition');
    body_json.value = body_json_builder;
    contact_json.value = contact_json_str != null ? contact_json_str : "";
    if (!feedback_definition.value) {
        feedback_definition.value = "[]";
    }
}