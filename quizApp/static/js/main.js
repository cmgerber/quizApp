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

$("#search-button").on('click', function(e) {
  respond_to_event();
});

$("#search-text").on('typeahead:cursorchanged typeahead:autocompleted', function (e, datum) {
    cur_obj = datum;
    full_val = true;
});

$("#search-text").on('typeahead:selected', function(e, datum) {
  var page = '';
  if (datum.type == 'cond') {
    page = 'condition';
  } else {
    page = 'institution';
  }
  window.open($SCRIPT_ROOT + page + "?" + datum.type + "=" + datum.value, "_self");
})







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


// start button action
$("#quiz-start-area").on('click', "#quiz-button", function (e) {
  $.getJSON( $SCRIPT_ROOT + "_quizStart", function(e) {
    $('#quiz-start-label').text('Begin ' + e.progress);
    $('#quiz-start-modal').modal('show');
  });
});

//start quiz modal button

$("#quiz-start-begin").on("click", function(e) {
  $.getJSON( $SCRIPT_ROOT + "_quizStart", function(e) {
      var newWindow = window.open($SCRIPT_ROOT + e.progress, "_self");
      });
  });

//****************
//PRETEST
//****************

$("#pretest-start-button").on("click", function(e) {
        replace_html();
  });

//pretest dropdown
// update distance dropdown text based on selection
$("body").delegate(".pretest-drop1-val", "click", function(e) {
  $("#pretest-drop1 button").html($(this).text() + ' <span class="caret"></span>');
});

$("body").delegate(".pretest-drop2-val", "click", function(e) {
  $("#pretest-drop2 button").empty().append($(this).text() + ' <span class="caret"></span>');
});

$("body").delegate(".pretest-drop3-val", "click", function(e) {
  $("#pretest-drop3 button").empty().append($(this).text() + ' <span class="caret"></span>');
});

//next button click
$('#pretest-next').on('click', function() {
  //get answers and write them to db
  var best1 = $("#pretest-drop1 button").text(),
      best2 = $("#pretest-drop2 button").text(),
      best3 = $("#pretest-drop3 button").text(),
      order = getParameterByName('order');

  $.getJSON($SCRIPT_ROOT + "_pretest_answers", {
    best1:best1,
    best2:best2,
    best3:best3,
    order:order
  }, function(data) {
    setTimeout(function() {
      replace_html();
    }, 1000);
  }
  );

});


//**********
//TRAINING
//**********

$("#training-start-button").on("click", function(e) {
        replace_html();
  });

//for rating drop downs
$("body").delegate(".training-rating1-val", "click", function(e) {
  $("#training-rating1 button").html($(this).text() + ' <span class="caret"></span>');
});

$("body").delegate(".training-rating2-val", "click", function(e) {
  $("#training-rating2 button").empty().append($(this).text() + ' <span class="caret"></span>');
});

$("body").delegate(".training-rating3-val", "click", function(e) {
  $("#training-rating3 button").empty().append($(this).text() + ' <span class="caret"></span>');
});

//next button click
$('#pretest-next').on('click', function() {
  //get answers and write them to db
  var best1 = getParameterByName('question_type') == 'rating' ? $("#training-rating1 button").text(): $("#training-drop1 button").text(),
      best2 = getParameterByName('question_type') == 'rating' ? $("#training-rating2 button").text(): $("#training-drop2 button").text(),
      best3 = getParameterByName('question_type') == 'rating' ? $("#training-rating3 button").text(): $("#training-drop3 button").text(),
      order = getParameterByName('order');

  $.getJSON($SCRIPT_ROOT + "_training_answers", {
    best1:best1,
    best2:best2,
    best3:best3,
    order:order
  }, function(data) {
    setTimeout(function() {
      replace_html();
    }, 1000);
  }
  );

});


//**********
//QUESTION CREATION
//**********

function replace_html() {

  var dropdown1 ='<div id="pretest-drop1" class="btn-group form-inline">'+
                '<button type="button" class="btn btn-primary">Graph</button>'+
                '<button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">'+
                  '<span class="caret"></span>'+
                '</button>'+
                '<ul class="dropdown-menu" role="menu">'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="pretest-drop1-val">Graph 1</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="pretest-drop1-val">Graph 2</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="pretest-drop1-val">Graph 3</a></li>'+
                '</ul>'+
              '</div>';
  var dropdown2 ='<div id="pretest-drop2" class="btn-group form-inline">'+
                '<button type="button" class="btn btn-primary">Graph</button>'+
                '<button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">'+
                  '<span class="caret"></span>'+
                '</button>'+
                '<ul class="dropdown-menu" role="menu">'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="pretest-drop2-val">Graph 1</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="pretest-drop2-val">Graph 2</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="pretest-drop2-val">Graph 3</a></li>'+
                '</ul>'+
              '</div>';
  var dropdown3 ='<div id="pretest-drop3" class="btn-group form-inline">'+
                '<button type="button" class="btn btn-primary">Graph</button>'+
                '<button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">'+
                  '<span class="caret"></span>'+
                '</button>'+
                '<ul class="dropdown-menu" role="menu">'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="pretest-drop3-val">Graph 1</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="pretest-drop3-val">Graph 2</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="pretest-drop3-val">Graph 3</a></li>'+
                '</ul>'+
              '</div>';
  var rating1 ='<div id="training-rating1" class="btn-group form-inline">'+
                '<button type="button" class="btn btn-primary">na</button>'+
                '<button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">'+
                  '<span class="caret"></span>'+
                '</button>'+
                '<ul class="dropdown-menu" role="menu">'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating1-val">0</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating1-val">1</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating1-val">2</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating1-val">3</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating1-val">4</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating1-val">5</a></li>'+
                '</ul>'+
              '</div>';
  var rating2 ='<div id="training-rating2" class="btn-group form-inline">'+
                '<button type="button" class="btn btn-primary">na</button>'+
                '<button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">'+
                  '<span class="caret"></span>'+
                '</button>'+
                '<ul class="dropdown-menu" role="menu">'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating2-val">0</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating2-val">1</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating2-val">2</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating2-val">3</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating2-val">4</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating2-val">5</a></li>'+
                '</ul>'+
              '</div>';
  var rating3 ='<div id="training-rating3" class="btn-group form-inline">'+
                '<button type="button" class="btn btn-primary">na</button>'+
                '<button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">'+
                  '<span class="caret"></span>'+
                '</button>'+
                '<ul class="dropdown-menu" role="menu">'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating3-val">0</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating3-val">1</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating3-val">2</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating3-val">3</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating3-val">4</a></li>'+
                  '<li><a role="menuitem" tabindex="-1" href="#" onClick="return false;" class="training-rating3-val">5</a></li>'+
                '</ul>'+
              '</div>';

    $.getJSON( $SCRIPT_ROOT + "first_question", function(d) {
        if(d.progress == 'pre_test' || d.progress == 'post_test'){
          //remove start button
          $('#pretest-start-area').remove();
          //add the three graphs
          $('#graph1').empty().append(d.graph1+
                            '<p>Graph 1</p>');
          $('#graph2').empty().append(d.graph2+
                            '<p>Graph 2</p>');
          $('#graph3').empty().append(d.graph3+
                            '<p>Graph 3</p>');
            //add the question
            $('#pretest-question').empty().append('<h3>'+d.question+'</h3>');
            $('#pretest-question').append('<br><p>Best Graph</p>'+dropdown1+
                                          '<br><br><p>Second Best Graph</p>'+dropdown2+
                                          '<br><br><p>Third Best Graph</p>'+dropdown3);

          //add next button
          $('#pretest-next').empty().append('<button id="pretest-next" type="button" class="btn btn-primary" data-dismiss="modal">Next</button>');
        }else{
          //remove start button
          $('#training-start-area').remove();
          //add the three graphs
          $('#graph1').empty().append(d.graph1+
                            '<p>Graph 1</p>');
          if(d.question_type == 'rating') {
            //add the question
            $('#training-question').empty().append('<h3>'+d.question+'</h3>');
            $('#training-question').append('<br><p>Graph 1</p>'+rating1+
                                          '<br><br><p>Graph 2</p>'+rating2+
                                          '<br><br><p>Graph 3</p>'+rating3);
          }else{
            //add the question
            $('#training-question').empty().append('<h3>'+d.question+'</h3>');
            $('#training-question').append('<br><p>Best Graph</p>'+dropdown1+
                                          '<br><br><p>Second Best Graph</p>'+dropdown2+
                                          '<br><br><p>Third Best Graph</p>'+dropdown3);
          }
          //add next button
          $('#training-next').empty().append('<button id="training-next" type="button" class="btn btn-primary" data-dismiss="modal">Next</button>');
        }
    });
}


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

// structure criteria jump
$("#structure-criteria-btn").on("click", function(e) {
  $("#goto-criteria-modal").modal('show');
})

$("#goto-criteria-ok").on("click", function(e) {
  function redir(admin) {
      var nct_id = getParameterByName('nct_id');
      window.open($SCRIPT_ROOT + "structure_trial_criteria?nct_id=" + nct_id, "_self");
      return false;
  }
  loginCheck(redir, "Whoops, you need to log in before you can use that tool.");
});

$("#goto-criteria-enter").on("click", function(e) {
  $("#create-concept-modal").modal('show');
  $("#goto-criteria-modal").modal('hide');
});

// accepting MeSH term suggestions interaction
$("#add-mesh-btn").on('click', function(e) {
  loginCheck(function(admin) {
    $("#add-mesh-modal").modal('show');
    $("#add-mesh-submit").on("click", function(g) {
      var nct_id = getParameterByName('nct_id'),
          cond_ids = [];
      $.each($("input[name='add-mesh-term']:checked"), function() {
        cond_ids.push($(this).val());
      });
      $.getJSON($SCRIPT_ROOT + "_mesh_stage", {
        cond_ids: JSON.stringify(cond_ids),
        nct_id: nct_id
      }, function(data) {
        if (data.done) {
          $("#add-mesh-modal .modal-body").html("<p>Your contribution will be reviewed by an administrator.</p>");
        } else {
          $("#add-mesh-modal .modal-body").html("<p>There is a problem. Please try again later.</p>");
        }
        $("#add-mesh-submit").remove();
        $("#add-mesh-modal .modal-footer").append('<button id="add-mesh-finish" type="button" class="btn btn-success" data-dismiss="modal">OK</button>');
        $("#add-mesh-finish").on('click', function(e) {
          $("#add-mesh-modal").modal('hide');
        })
      });
      return false;
    });
  }, "Whoops, you need to log in before you can tag trials with additional conditions.")
});






// tool interactions
$('#create-concept-modal').on('shown.bs.modal', function () {
    $('#create-concept-modal #input-new-concept').focus();
})

$('#create-concept-submit').on('click', function(e){
  function redir(admin) {
      var initial_term = $("#create-concept-modal #input-new-concept").val();
      window.open($SCRIPT_ROOT + "active_learning?term=" + initial_term, "_self");
      return false;
  }
  if ($("#create-concept-modal #input-new-concept").val().length > 1) {
    loginCheck(redir, "Whoops, you need to log in before you can use that tool.");
    $("#create-concept-modal").modal('hide');
  } else {
    clearVals();
    alert('You must enter a term longer than one character. Please try again.');
  }
});

$("#create-concept-modal .form-control").keydown(function(e) {
  function redir(admin) {
      var initial_term = $("#create-concept-modal #input-new-concept").val();
      window.open($SCRIPT_ROOT + "active_learning?term=" + initial_term, "_self");
      return false;
  }
  if (e.keyCode == 13) {
      if ($("#create-concept-modal #input-new-concept").val().length > 1) {
        loginCheck(redir, "Whoops, you need to log in before you can use that tool.");
        $("#create-concept-modal").modal('hide');
      } else {
        clearVals();
        alert('You must enter a term longer than one character. Please try again.');
      }
      return false;
    }
});

$('#create-concept-cancel').on('click', function(e){clearVals()} );

// admin tools jump
$("#pick-admin-tool").on("click", function(e) {
  function redir(admin) {
      if (admin == 1) {
        $.getJSON($SCRIPT_ROOT + "_get_admin_counts", {}, function(data) {
          $("#admin-select-num-concepts").text(data.num_concepts + " concept" + (data.num_concepts > 1 ? "s" : "") + " to review");
          $("#admin-select-num-mesh").text(data.num_mesh + " assignment" + (data.num_mesh > 1 ? "s" : "") + " to review");
          $("#admin-select-modal").modal('show');
        })
      } else {
        alert("Sorry, you need to have administrator privileges to use these tools.");
      }
      return false;
  }
  loginCheck(redir, "Whoops, you need to log in before you can use that tool.");
});









// MeSH suggestion interactions
$("#submit-suggestion-text").on('click', function(e) {
  var thisdoc = $("#mesh-text").val();
  console.log(JSON.stringify(thisdoc).length);
  if (thisdoc.length > 0) {
    var header = '<h4>Retrieving suggestions...</h4>',
        spinner = '<i id="top-cond-spinner" class="fa fa-spinner fa-pulse" style="font-size: 5em; margin: .5em;"></i>';
    $("#results-pane").html(header + spinner);
    $.getJSON($SCRIPT_ROOT + '_get_suggestions', {doc: thisdoc}, function(data) {
      $("#results-pane").empty();
      var write_html = '';
      if (data.results) {
        write_html = "<h5>Suggested terms</h5><ul class='nodisc'>";
        for (i=0; i<data.results.length; i++) {
          write_html += "<li><a href='http://www.nlm.nih.gov/cgi/mesh/2015/MB_cgi?mode=&term=" + data.results[i] +
                        "' target='_blank'>" + data.results[i] + "</li>";
        }
        write_html += "</ul>"
      } else {
        write_html = '<p>Sorry, no results were returned</p>';
      }
      $("#results-pane").html(write_html);
    })
  }

})






// Criteria concept approvals








