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
