/* Not-a-quiz quiz */
(function($){
  $.fn.quiz = function( options ){
    var questions = $('.quiz').length;
    var answered = 0;

    var win = options.onWin || function(){};
    
    $('.quiz .discussion').hide();
    /* For each quiz slide... */
    $('.quiz').each(function(){
      var discussion = $('.discussion', this);
      /* Show the discussion when they click the right answer */
      $('.options', this).one('click', function(evt){
        if($(evt.target).hasClass('correct'))
          $('.answer', discussion).text("That's right!");
        else 
          $('.answer', discussion).text("That's wrong!");
        discussion.fadeIn();          
        answered++;
        if (answered == questions) {
          win();
        }
      });
    });
  }
})(jQuery);
