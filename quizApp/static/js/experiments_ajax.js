function create_experiment_data(form) {
    var formData = {
      'name' : $('input[name=name]').val(),
      'start': $('input[name=start]').val(),
      'stop': $('input[name=stop]').val(),
    };
    return formData;
}

function create_experiment_done(data) {
    console.log(data);
    $('#exp_table tr:last').before(data);
}

function add_remove_activity_data(form) {
  checked_boxes = $('input:checked', form);

  if(!checked_boxes.size()) {
    alert("Please make a selection.");
    return 0;
  }

  var formData = {'activities': []};

  $("input:checked", form).each(function() {
    formData["activities"].push($(this).val());
  });
  return formData;
}

function add_remove_activity_done(data) {
  console.log(data);
  if(data.success) {
    window.location.reload();
  }
}

function delete_experiment_data(form) {
  return {};
}

function delete_experiment_done(data) {
  console.log(data);
  if(data.success) {
    window.location.href = data["next_url"];
  }
}

function question_submit_data(form) {
  checked_box = $('input:checked');

  if(!checked_box.size()) {
    alert("Please make a selection");
    return 0;
  }

  var formData = {
    'choices': checked_box[0].getAttribute("value"),
    'reflection': $("#reflection").val()
  };
  return formData;
}

function question_submit_done(data) {
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
}

$(document).ready(function() {
  form_ajax("#create-form", create_experiment_data, create_experiment_done);
  form_ajax("#activity-remove-form,#activity-add-form",
      add_remove_activity_data, add_remove_activity_done);
  form_ajax("#experiment-delete-form", delete_experiment_data,
      delete_experiment_done);
  form_ajax("#question-submit-form", question_submit_data,
      question_submit_done);
});
