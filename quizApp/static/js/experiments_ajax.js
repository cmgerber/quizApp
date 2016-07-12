function create_experiment_done(data) {
  console.log(data);
  $('#exp_table tr:last').before(data);
}

function add_remove_activity_done(data) {
  console.log(data);
  if(data.success) {
    window.location.reload();
  }
}

function delete_experiment_data(form) {
  return $(form).serialize()
    var fields = get_fields(form);
  return {};
}

function delete_experiment_done(data) {
  console.log(data);
  if(data.success) {
    window.location.href = data["next_url"];
  }
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
  form_ajax("#create-experiment-form", create_experiment_done);
  form_ajax("#activity-remove-form,#activity-add-form",
      add_remove_activity_done);
  form_ajax("#experiment-delete-form", delete_experiment_done);
  form_ajax("#question-submit-form", question_submit_done);
});
