var csrftoken = $('meta[name=csrf-token]').attr('content')

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            var csrftoken = $('meta[name=csrf-token]').attr('content')
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
})

$(document).ready(function() {
    $('#create-form').submit(function(event) {
        var formData = {
            'name' : $('input[name=name]').val(),
            'start': $('input[name=start]').val(),
            'stop': $('input[name=stop]').val(),
        };

        $.ajax({
            type: 'POST',
            contentType: "application/json",
            url: $('form[id=create-form]').attr("action"),
            data: JSON.stringify(formData),
            dataType: 'json',
            encode: true
        })

            .done(function(data) {
                console.log(data);
                if(data.success) {
                    $('#exp_table tr:last') //ugh, hardcoding
                        .before("<tr><td>" + formData.name + "</td>" +
                                "<td>" + formData.start + "</td>" +
                                "<td>" + formData.stop + "</td>" +
                                "<td></td>" +
                                "<td></td></tr>")
                }
            });

        event.preventDefault();
    });

    $('.delete-form').submit(function(event) {
        var formData = {
            'id' : $(this).find("input[name=exp_id]").val(),
        };

        $.ajax({
            type: 'POST',
            contentType: "application/json",
            url: this.getAttribute("action"),
            data: JSON.stringify(formData),
            dataType: 'json',
            encode: true
        })

            .done(function(data) {
                console.log(data);
                if(data.success) {
                    $("#row-" + data.id).remove()
                }
            });

        event.preventDefault();
    });
});
