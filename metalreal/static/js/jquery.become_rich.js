(function($){
  $.fn.become_rich = function(){
    this.each(function(){
      var $this = $(this),
          self = this,
          selection = '',
          caretPosition = -1,
          $toolbar = $('<div class="btn-group become-rich-toolbar"> \
                  <div class="btn make-increase" data-make="increase" >H<i class="icon-plus" title="Increse font size"></i></div> \
                  <div class="btn make-decrease" data-make="decrease" >H<i class="icon-minus" title="Decrease font size"></i></div> \
                  <div class="btn make-bold" data-make="bold" ><i class="icon-bold" title="Bold" ></i></div> \
                  <div class="btn make-italic" data-make="italic" ><i class="icon-italic" title="Italic"></i></div> \
                  <div class="btn make-hr" data-make="hr" >__</div> \
                  <div class="btn make-list" data-make="list" ><i class="icon-list" title="List"></i></div> \
                  <div class="btn make-link" data-make="link" ><i class="icon-globe"></i> Link</div> \
                  <div class="btn add-question" data-toggle="modal" data-make="question" > \
                    <i class="icon-question-sign" title="Qustion"></i> Question \
                  </div> \
                  <div class="btn make-quiz" data-make="quiz" ><i class="icon-check" title="Quiz"></i> Quiz</div> \
                </div>');

      if($this.parent().has('.become-rich-toolbar').length == 0){
        $this.before($toolbar);
        $toolbar.children('.btn').bind('click', function(e){
          self.makeChange($(e.currentTarget).data('make'));
        });
        // Auto insert 2 spaces when press Enter
        $this.keypress(function(e){
          if(e.keyCode == 13){
            this.getSelection();
            this.insert('  \n');
            e.preventDefault();
            this.setSelection(caretPosition + 3, 0);
          }
        });
      }

      this.makeChange = function(what, question_id){
        var block = this.getSelection();
        switch(what){
          case 'bold':
            block = '**' + block + '**';
            break;
          case 'italic':
            block = '*' + block + '*';
            break;
          case 'hr':
            block = block + '\n- - -\n';
            break;
          case 'link':
            block = '[' + block + '](http://www.yourlinkhere.com)';
            break;
          case 'question':
            if(question_id){
              block = '[question=' + question_id + ']';
            }
            break;
        }
        this.insert(block);
        this.setSelection(caretPosition + block.length, 0);
      }


      this.insert = function(block) {  
        if (document.selection) {
          var newSelection = document.selection.createRange();
          newSelection.text = block;
        } else {
          self.value =  self.value.substring(0, caretPosition)  + block + self.value.substring(caretPosition + selection.length, self.value.length);
        }
      }

      this.setSelection = function(start, len) {
        if (self.createTextRange){
          // quick fix to make it work on Opera 9.5
          if ($.browser.opera && $.browser.version >= 9.5 && len == 0) {
            return false;
          }
          range = self.createTextRange();
          range.collapse(true);
          range.moveStart('character', start); 
          range.moveEnd('character', len); 
          range.select();
        } else if (self.setSelectionRange ){
          self.setSelectionRange(start, start + len);
        }
        self.focus();
      }

      this.getSelection = function(){
        self.focus();

        if (document.selection) {
          selection = document.selection.createRange().text;
          if ($.browser.msie) { 
            var range = document.selection.createRange(), rangeCopy = range.duplicate();
            rangeCopy.moveToElementText(self);
            caretPosition = -1;
            while(rangeCopy.inRange(range)) {
              rangeCopy.moveStart('character');
              caretPosition ++;
            }
          } else { 
            caretPosition = self.selectionStart;
          }
        } else { 
          caretPosition = self.selectionStart;

          selection = self.value.substring(caretPosition, self.selectionEnd);
        } 
        return selection;
      }
    });

  }
})(jQuery);