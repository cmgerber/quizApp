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

//next button click
$('#pretest-next').on('click', function() {
  //get answers and write them to db
  var best1 = $("input[type='radio'][name='Q1']:checked").attr('id'),
      best2 = $("input[type='radio'][name='Q2']:checked").attr('id'),
      best3 = $("input[type='radio'][name='Q3']:checked").attr('id'),
      order = getParameterByName('order');

      console.log(best1, best2, best3);

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

//next button click
$('#training-next').on('click', function() {
  console.log($("#training-question-answers input[type='radio']:checked").attr('id'));
  console.log($("#training-rating1 input[type='radio']:checked").attr('id'));
  //get answers and write them to db
  var rating1 = $("input[type='radio'][name='training-rating1']:checked").attr('id'),
      best1 = $("input[type='radio'][name='training-question-answers']:checked").attr('id');
  //  if (getParameterByName('question_type') == 'rating') {
  //     best1 = $("#training-rating1 button").text();
  // }else {
  //  best1 = $("#training-question-answers input[type='radio']:checked").attr('id');
  // }
  var order = getParameterByName('order');
  console.log(rating1);

  $.getJSON($SCRIPT_ROOT + "_training_answers", {
    best1:best1,
    order:order,
    rating1:rating1
  }, function(data) {
    setTimeout(function() {
      replace_html();
    }, 1000);
  }
  );

});


//**********
//POSTTEST
//**********

$("#post-start-button").on("click", function(e) {
        replace_html();
  });

//next button click
$('#post-next').on('click', function() {
  //get answers and write them to db
  var best1 = $("input[type='radio'][name='Q1']:checked").attr('id'),
      best2 = $("input[type='radio'][name='Q2']:checked").attr('id'),
      best3 = $("input[type='radio'][name='Q3']:checked").attr('id'),
      best4 = $("#posttest-comment-text").val(),
      order = getParameterByName('order');

      console.log(best1, best2, best3, best4);

  $.getJSON($SCRIPT_ROOT + "_pretest_answers", {
    best1:best1,
    best2:best2,
    best3:best3,
    best4:best4,
    order:order
  }, function(data) {
    setTimeout(function() {
      replace_html();
    }, 1000);
  }
  );

});

//next button click
$('#posttest-next').on('click', function() {
  //get answers and write them to db
  var best1 = $("input[type='radio'][name='posttest-question-answers']:checked").attr('id'),
      best2 = $("input[type='radio'][name='posttest2-question-answers']:checked").attr('id');

  var order = getParameterByName('order');

  $.getJSON($SCRIPT_ROOT + "_posttest_answers", {
    best1:best1,
    best2:best2,
    order:order
  }, function(data) {
    window.open($SCRIPT_ROOT + "donedone", "_self");
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
        if(d.progress == 'next') {
          window.open($SCRIPT_ROOT + "next", "_self");
        }
        if(d.progress == 'done') {
          window.open($SCRIPT_ROOT + "done", "_self");
        }
        if(d.progress == 'pre_test'){
          //remove start button
          $('#pretest-start-area').remove();
          //add the three graphs
          var img_pre = "<img src='"
          var img_post = "'/>"
          $('#graph1').empty().append(img_pre + d.graphs[0] + img_post +
                            '<p>Graph 1</p>');
          $('#graph2').empty().append(img_pre + d.graphs[1] + img_post +
                            '<p>Graph 2</p>');
          $('#graph3').empty().append(img_pre + d.graphs[2] + img_post +
                            '<p>Graph 3</p>');
            //add the question
            $('#pretest-question').empty().append('<h3>'+d.question+'</h3>');
            $('#pretest-question').append('<br><p>Best Graph</p>'+
                                          '<br><div id="pretest-drop1" class="btn-group" data-toggle="buttons">'+
                                            '<label class="btn btn-primary">'+
                                            '<input type="radio" name="Q1" id="Graph 1"> Graph 1 </label>'+
                                            '<label class="btn btn-primary">'+
                                          '<input type="radio" name="Q1" id="Graph 2"> Graph 2 </label>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="Q1" id="Graph 3"> Graph 3 </label></div>'+
                                          '<br><br><p>Second Best Graph</p>'+
                                          '<br><div id="pretest-drop2" class="btn-group" data-toggle="buttons">'+
                                            '<label class="btn btn-primary">'+
                                            '<input type="radio" name="Q2" id="Graph 1"> Graph 1 </label>'+
                                            '<label class="btn btn-primary">'+
                                          '<input type="radio" name="Q2" id="Graph 2"> Graph 2 </label>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="Q2" id="Graph 3"> Graph 3 </label></div>'+
                                          '<br><br><p>Third Best Graph</p>'+
                                          '<br><div id="pretest-drop3" class="btn-group" data-toggle="buttons">'+
                                            '<label class="btn btn-primary">'+
                                            '<input type="radio" name="Q3" id="Graph 1"> Graph 1 </label>'+
                                            '<label class="btn btn-primary">'+
                                          '<input type="radio" name="Q3" id="Graph 2"> Graph 2 </label>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="Q3" id="Graph 3"> Graph 3 </label></div>');

          //add next button
          $('#pretest-next').empty().append('<button id="pretest-next" type="button" class="btn btn-primary" data-dismiss="modal">Next</button>');
        } else if(d.progress == 'post_test'){
          //remove start button
          $('#post-start-area').remove();
          //add the three graphs
          $('#graph1').empty().append(d.graph1+
                            '<p>Graph 1</p>');
          $('#graph2').empty().append(d.graph2+
                            '<p>Graph 2</p>');
          $('#graph3').empty().append(d.graph3+
                            '<p>Graph 3</p>');
            //add the question
            $('#post-question').empty().append('<h3>'+d.question+'</h3>');
            $('#post-question').append('<br><p>Best Graph</p>'+
                                          '<br><div id="post-drop1" class="btn-group" data-toggle="buttons">'+
                                            '<label class="btn btn-primary">'+
                                            '<input type="radio" name="Q1" id="Graph 1"> Graph 1 </label>'+
                                            '<label class="btn btn-primary">'+
                                          '<input type="radio" name="Q1" id="Graph 2"> Graph 2 </label>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="Q1" id="Graph 3"> Graph 3 </label></div>'+
                                          '<br><br><p>Second Best Graph</p>'+
                                          '<br><div id="post-drop2" class="btn-group" data-toggle="buttons">'+
                                            '<label class="btn btn-primary">'+
                                            '<input type="radio" name="Q2" id="Graph 1"> Graph 1 </label>'+
                                            '<label class="btn btn-primary">'+
                                          '<input type="radio" name="Q2" id="Graph 2"> Graph 2 </label>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="Q2" id="Graph 3"> Graph 3 </label></div>'+
                                          '<br><br><p>Third Best Graph</p>'+
                                          '<br><div id="post-drop3" class="btn-group" data-toggle="buttons">'+
                                            '<label class="btn btn-primary">'+
                                            '<input type="radio" name="Q3" id="Graph 1"> Graph 1 </label>'+
                                            '<label class="btn btn-primary">'+
                                          '<input type="radio" name="Q3" id="Graph 2"> Graph 2 </label>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="Q3" id="Graph 3"> Graph 3 </label></div><br><br>');
            $('#post-question').append('<div id="post-comment1" class="form-group">'+
                                            '<label for="comment">Briefly describe your reasoning for this ranking:</label>'+
                                            '<textarea class="form-control" rows="5" id="posttest-comment-text"></textarea>'+
                                          '</div>');

          //add next button
          $('#post-next').empty().append('<button id="post-next" type="button" class="btn btn-primary" data-dismiss="modal">Next</button>');
        }else{
          //remove start button
          $('#training-start-area').remove();
          //add the three graphs
          $('#graph1').empty().append(d.graph1+
                            '<p>Graph 1</p>');
          if(d.question_type == 'rating') {
            //add the question
            $('#training-question').empty().append('<h3>'+d.question+'</h3>');
            $('#training-question').append('<br><div id="training-question-answers" class="btn-group" data-toggle="buttons">'+
                                            '<label class="btn btn-primary">'+
                                            '<input type="radio" name="training-rating1" id="1"> 1 </label>'+
                                            '<label class="btn btn-primary">'+
                                          '<input type="radio" name="training-rating1" id="2"> 2 </label>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="training-rating1" id="3"> 3 </label>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="training-rating1" id="4"> 4 </label>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="training-rating1" id="5"> 5 </label>'+'</div>');
          } else if(d.question_type == 'heuristic'){
            $('#training-question').empty().append('<h3>'+d.question+'</h3>');
            $('#training-question').append('<div id="training-question-answers" class="btn-group" data-toggle="buttons">'+
                                            '<label class="btn btn-primary">'+
                                            '<input type="radio" name="training-question-answers" id="optionA"> 1 </label>'+
                                            d.answer1+'<br><br>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="training-question-answers" id="optionB"> 2 </label>'+
                                          d.answer2+'<br><br>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="training-question-answers" id="optionC"> 3 </label>'+
                                          d.answer3+'<br><br>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="training-question-answers" id="optionD"> 4 </label>'+
                                          d.answer4+'<br><br>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="training-question-answers" id="optionE"> 5 </label>'+
                                          d.answer5+'<br><br>'+'</div>');
          } else{
            //add the question
            $('#training-question').empty().append('<h3>'+d.question+'</h3>');
            $('#training-question').append('<div id="training-question-answers" class="btn-group" data-toggle="buttons">'+
                                            '<label class="btn btn-primary">'+
                                            '<input type="radio" name="training-question-answers" id="optionA"> A </label>'+
                                            d.answer1+'<br><br>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="training-question-answers" id="optionB"> B </label>'+
                                          d.answer2+'<br><br>'+
                                          '<label class="btn btn-primary">'+
                                          '<input type="radio" name="training-question-answers" id="optionC"> C </label>'+
                                          d.answer3+'<br><br>'+'</div>');

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

