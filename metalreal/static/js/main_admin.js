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
});