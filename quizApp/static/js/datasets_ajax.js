$(document).ready(function() {
  form_ajax("#create-dataset-form", done_refresh);
  form_ajax("#update-dataset-form", done_refresh);
  form_ajax("#delete-dataset-form", done_redirect);
  form_ajax("#delete-graph-form", done_refresh);

  $('#preview-graph-modal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var row = button.parent().parent();
    var name = $(".graph-name", row).text()
    var filename = $(".graph-filename", row).text()
    var read_url = $(button).data("read-url");
    var delete_url = $(button).data("delete-url");

    var modal = $(this);
    modal.find('.modal-title').text('Preview graph ' + name);
    modal.find('#delete-graph-form').attr("action", delete_url)

    $.ajax({
      type: "get",
      url: read_url,
      encode: true,
    })
    .done(function(data) {
      console.log(data);
      $('#preview-graph-modal .modal-body').html(data);
    });

  })
})
