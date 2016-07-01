// check login to update box
$.getJSON( $SCRIPT_ROOT + "_check_login", {}, function( data ) {
    if (data.logged_in && !($("#logged-in-area").length > 0)) {
      changeButtons(data.username);
      return false;
    }
});


function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

var substringMatcher = function(strs) {
  return function findMatches(q, cb) {
    var matches, substrRegex;

    // an array that will be populated with substring matches
    matches = [];

    // regex used to determine if a string contains the substring `q`
    substrRegex = new RegExp(q, 'i');

    // iterate through the pool of strings and for any string that
    // contains the substring `q`, add it to the `matches` array
    $.each(strs, function(i, str) {
      if (substrRegex.test(str)) {
        // the typeahead jQuery plugin expects suggestions to a
        // JavaScript object, refer to typeahead docs for more info
        matches.push({ value: str });
      }
    });

    cb(matches);
  };
};




var cur_obj = {},
    full_val = false;

function respond_to_event() {
  if (full_val) {
    var page = '';
    if (cur_obj.type == 'cond') {
      page = 'condition';
    } else {
      page = 'institution';
    }
    window.open($SCRIPT_ROOT + page + "?" + cur_obj.type + "=" + cur_obj.value, "_self");
    return false;
  } else {
    var cur_str = $('#search-text').val();
    if (cur_str.length > 0) {
      window.open($SCRIPT_ROOT + "search_results?q=" + cur_str, "_self");
      return false;
    }
  }
}

$("#search-text").keydown(function(event) {
    if (event.keyCode == 13) {
      respond_to_event();
      } else {
        cur_obj = {};
        full_val = false;
      }
});

// clearing input vals info
function clearVals() {
  $(".form-control").val('');
};

function clearUserPass() {
  $("#input-username").val('');
  $("#input-password").val('');
}

// replacing login buttons with username and logout button
function changeButtons(username) {
  $('#create-acct-button').remove();
  $('#login-button').remove();
  $('#login-area').append('<div id="logged-in-area"><small>Logged in as <strong>' + username + '</strong><small>&nbsp;' +
      '<button id="logout-button" type="button" class="btn btn-danger btn-xs">Logout</button></div>');
  $('#quiz-start-area').append('<div id="logged-in-quiz"><button id="quiz-button" type="button" class="btn btn-primary">Start</button></div>');
}


// main user login interaction
function loginUser(e) {
  $.getJSON( $SCRIPT_ROOT + "_login", {
      username: $("#login-modal #input-username").val()
    }, function( data ) {
    clearVals();
    if (data.result == 'ok') {
      changeButtons(data.username);
    } else {
      alert("Id doesn't match any existing accounts. Please try again.");
    }
  });
}

$('#login-modal').on('shown.bs.modal', function () {
    $('#login-modal #input-username').focus();
})

$('#login-submit').on('click', function(e){loginUser(e)} );

$("#login-modal .form-control").keydown(function(e) {
    if (e.keyCode == 13) {
        if ($("#login-modal #input-username").val().length > 0) {
          loginUser(e);
          $("#login-modal").modal('hide');
        } else {
          alert('Id must be present in order to log in! Please try again.');
        }
        return false;
      }
});

$('#login-cancel').on('click', function(e){clearVals()} );

// logout button action
$("#login-area").on('click', "#logout-button", function (e) {
  $.getJSON( $SCRIPT_ROOT + "_logout", function(e) {
    $("#logged-in-area").remove();
    $('#login-area').append(' <button id="login-button" type="button" ' +
        'class="btn btn-success btn-xs" data-toggle="modal" data-target="#login-modal">Login</button>');
  });
});

// check login and alert or redirect as necessary
function OpenInNewTab(url) {
  var win = window.open(url, '_blank');
  win.focus();
}

function loginCheck(ok_fcn, warn_msg) {
  $.getJSON( $SCRIPT_ROOT + "_check_login", {}, function( data ) {
    if (data.logged_in) {
      ok_fcn(data.progress);
    } else {
      alert(warn_msg);
    }
  });
}
