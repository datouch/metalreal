$(document).ready(function(){
  window.previewState = false;
  window.counter = 0;
  window.dotted = ['', '.', '..', '...'];
  window.intervalID = 0;

  $('.tabbable li:not(:nth-child(2)) a').click(function(e){
    e.preventDefault();
    $(this).tab('show');
  });

  $('.tabbable li:nth-child(2) a').click(function(e){
    e.preventDefault();

    if(!previewState){
      var that = this;
      $(this).html('Processing');
      intervalID = setInterval(function(){
        $(that).html('Processing' + dotted[counter % 4]);
        counter += 1;
      }, 300);
      previewState = true;
      $.post('/markdown_process', { markdown: $('textarea').val() }, function(data){
        $('#previewArea').html(data);
        previewState = false;
        clearInterval(intervalID);
        $(that).html('Preview');
        $(that).tab('show');
      });
    }
  });

  $('#make-bold').click(function(){
    var selection = window.getSelection();
    console.log(selection.toString());
  });

  $('#required_chapter').on('typeahead-complete', function(e, val){
    if($('#required_chapters').find('input[value="' + val.split(' ')[0] + '"]').length == 0){
      var html = "<input type='hidden' value='" + val.split(' ')[0] +
                  "' data-value='" + val + "'  name='required_chapters[]' />" +
                  "<div title='click to remove' class='required_chapters btn btn-info' data-value='"+
                  val + "' >" + val + " <i class='icon-trash icon-white'></i></div>"
      $('#required_chapters').append(html).find('div').tooltip();
    }
    $('#required_chapter').val('');
  });
  $('#required_chapters').delegate('div', 'click', function(){
    $('#required_chapters').find('input[data-value="'+$(this).data('value')+'"]').remove();
    $(this).tooltip('hide').remove();
  });
  $('#required_chapter').keydown(function(e, val){
    if(e.keyCode == 13){
      e.stopPropagation();
      e.preventDefault();
    }
  });

  $('#add-question').click(function(){
    if($('#question-modal form input[name="chapter_id"]').val() == ""){
      var html =  '<div class="alert fade in alert-error">' +
                    '<button class="close" data-dismiss="alert">×</button>' +
                    '<strong>You have to save chapter first!</strong>' +
                  '</div>';
      $(html).appendTo('.flashes');
      $('.alert').alert();
    }
    else {
      $('#question-modal').modal();
    }
  });

  $('#question-modal form').submit(function(e){
    e.stopPropagation();
    e.preventDefault();
    $.ajax({ url: $(this).attr('action'), 
             data: { question: $(this).find('input[name="question"]').val(),
                     answer: $(this).find('input[name="answer"]').val(),
                     type: $(this).find('input[name="type"]').val(),
                     hint: $(this).find('input[name="hint"]').val(),
                     chapter_id: $(this).find('input[name="chapter_id"]').val()}, 
             type: 'POST',
             dataType: 'json',
             success: function(data){
              $('#question-modal').modal('hide');
              var html =  '<div class="alert fade in alert-success">' +
                            '<button class="close" data-dismiss="alert">×</button>' +
                            '<strong>' + data.question + ' created with ID: ' + data.id + '</strong>' +
                          '</div>';
              $(html).appendTo('.flashes');
              $('.alert').alert();
             },
             error: function(){
              var html =  '<div class="alert fade in alert-error">' +
                            '<button class="close" data-dismiss="alert">×</button>' +
                            '<strong>Unable to create new question!</strong>' +
                          '</div>';
              $(html).appendTo('.flashes');
              $('.alert').alert();
             }
          });
  });
});