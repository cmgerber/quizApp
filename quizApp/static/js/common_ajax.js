$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
      var csrftoken = $('meta[name=csrf-token]').attr('content')
        xhr.setRequestHeader("X-CSRFToken", csrftoken)
    }
  }
})

function form_ajax(selector, get_data, done_callback) {
  $(selector).submit(function(event) {
    event.preventDefault();
    var formData = get_data(this);
    if(formData == 0) {
      return;
    }
    $.ajax({
      type: this.getAttribute("method"),
      contentType: "application/json",
      url: this.getAttribute("action"),
      data: JSON.stringify(formData),
      encode: true
    })
    .done(done_callback);
  });
}
