$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            var csrftoken = $('meta[name=csrf-token]').attr('content')
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
})

$(document).ready(function() {
    $(".btn-modify").click(function() {
        id = $(this.parentElement.parentElement).data("exp-id");
        $.ajax({
            type: "GET",
            url: "/experiments/" + id + "/modification_form",
            dataType: "html",
            encode: true
        })
        .done(function(data) {
            $("tr[data-exp-id=" + id + "]").replaceWith(data)
                console.log(data);
        })
    });

    $('.modify-form').submit(function(event) {
        $.ajax({
            type: "POST",
        })

        .done(function(data) {
            console.log(data);
        });
    })

    $('#create-form').submit(function(event) {
        var formData = {
            'name' : $('input[name=name]').val(),
            'start': $('input[name=start]').val(),
            'stop': $('input[name=stop]').val(),
        };
        var form = $('form[id=create-form]');
        $.ajax({
            type: form.attr("method"),
            contentType: "application/json",
            url: form.attr("action"),
            data: JSON.stringify(formData),
            dataType: 'html',
            encode: true
        })

        .done(function(data) {
            console.log(data);
            $('#exp_table tr:last').before(data);
        });

        event.preventDefault();
    });

    $('.delete-form').submit(function(event) {
        var formData = {
            'id' : $(this).find("input[name=exp_id]").val(),
        };

        $.ajax({
            type: this.getAttribute("method"),
            contentType: "application/json",
            url: this.getAttribute("action"),
            data: JSON.stringify(formData),
            dataType: 'json',
            encode: true
        })

        .done(function(data) {
            console.log(data);
            if(data.success) {
                $("*[data-exp-id=" + data.id + "]").remove()
            }
        });

        event.preventDefault();
    });

    $("#question-submit-form").submit(function(event) {
        event.preventDefault();
        checked_box = $('input:checked', this);

        if(!checked_box.size()) {
            alert("Please make a selection");
            return;
        }

        var formData = {
            'answers': checked_box[0].getAttribute("value"),
            'reflection': $("#reflection").val()
        };

        $.ajax({
            type: this.getAttribute("method"),
            contentType: "application/json",
            url: this.getAttribute("action"),
            data: JSON.stringify(formData),
            dataType: 'json',
            encode: true
        })

        .done(function(data) {
            console.log(data);
            if(data.success) {
                if(data.explanation) {
                    $("#explanation-container").css("display", "block");
                    $("#explanation-text").text(data.explanation);
                    $("#continue-link").attr("href", data.next_url);
                    $("#submit").remove();
                }
                else {
                    window.location.href = data["next_url"];
                }
            }
        });

    })
});
