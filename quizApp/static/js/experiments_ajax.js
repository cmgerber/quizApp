  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
        var csrftoken = $('meta[name=csrf-token]').attr('content')
          xhr.setRequestHeader("X-CSRFToken", csrftoken)
      }
    }
  })

  function replaceIdAndValue(id, val, obj) {
    obj.setAttribute("value", val);
    obj.setAttribute("id", id);
  }

  $(document).ready(function() {
    $(".btn-modify").click(function() {
      var row = this.parentElement.parentElement;
      var id = row.getAttribute("data-id");
      var name = $(row).find(".name > a").text();
      var start = $(row).find(".start").text();
      var stop = $(row).find(".stop").text();

      mod_form = $("#exp_table tr:last").clone();
    mod_form.find("form")[0].setAttribute("id", "modify-form-" + id);

    replaceIdAndValue("modify-name", name, mod_form.find("#name")[0]);
    replaceIdAndValue("modify-start", start, mod_form.find("#start")[0]);
    replaceIdAndValue("modify-stop", stop, mod_form.find("#stop")[0]);
    replaceIdAndValue("modify-submit", "Save", mod_form.find("#submit")[0]);

    $(this.parentElement.parentElement).replaceWith(mod_form)

  });

  $('#create-form').submit(function(event) {
    var formData = {
      'name' : $('input[name=name]').val(),
      'start': $('input[name=start]').val(),
      'stop': $('input[name=stop]').val(),
    };
    var form = $('form[id=create-form]')
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
        $("*[data-id=" + data.id + "]").remove()
      }
    });

    event.preventDefault();
  });
});
