$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
      var csrftoken = $('meta[name=csrf-token]').attr('content')
        xhr.setRequestHeader("X-CSRFToken", csrftoken)
    }
  }
})

function form_ajax(selector, done_callback) {
  $(selector).submit(function(event) {
    event.preventDefault();
    $.ajax({
      type: this.getAttribute("method"),
      url: this.getAttribute("action"),
      data: $(this).serialize(),
      encode: true,
    })
    .done(done_callback);
  });
}

// Some generic callbacks

function done_redirect(data) {
  console.log(data);
  if(data.success) {
    window.location.href = data["next_url"]
  } else {
    render_errors(data.errors);
  }

}

function done_refresh(data) {
  console.log(data);
  if(data.success) {
    window.location.reload();
  } else {
    render_errors(data.errors, data.prefix);
  }
}

function render_errors(errors, prefix) {
  if(!prefix) {
    prefix = ""
  }
  for(var id in errors) {
    if(errors.hasOwnProperty(id)) {
      var form_control = $("#" + prefix + id).parents(".form-group");
      form_control.addClass("has-error");
      form_control.children(".help-block").remove();
      form_control.append(error_to_html(errors[id]));
    }
  }
}

function error_to_html(text) {
  return "<p class='help-block'>" + text + "</p>";
}
