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

  $('#activity-remove-form').submit(function(event) {
    event.preventDefault();
    checked_boxes = $('input:checked', this);

    if(!checked_boxes.size()) {
      alert("Please make a selection.");
      return;
    }


    var formData = {'activities': []};

    $("input:checked", this).each(function() {
      formData["activities"].push($(this).val());
    });
          $.ajax({
            type: this.getAttribute("method"),
            contentType: "application/json",
            url: this.getAttribute("action"),
            data: JSON.stringify(formData),
            dataType: 'json',
            encode: true
          })
  })

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
