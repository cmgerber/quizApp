function create_experiment_done(data) {
  console.log(data);
  $('#exp_table tr:last').before(data);
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
  form_ajax("#update-experiment-form", done_refresh);
  form_ajax("#activity-remove-form, #activity-add-form", done_refresh);
  form_ajax("#experiment-delete-form", done_redirect);
  form_ajax("#question-submit-form", question_submit_done);
});
