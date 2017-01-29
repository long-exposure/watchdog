window.plugin = {
  name: 'Captures',
  loaded: 'capture_plugin_loaded'
};


function capture_plugin_loaded() {

	// load lightgallery jquery library async
	// $.getScript works sync and can not be used here!
	$.ajax({
        async: false,
        type: 'GET',
        url: '/javascript/lightGallery/dist/js/lightgallery.js',
        dataType: 'script'
    });

	$('head').append('<link rel="stylesheet" type="text/css" href="/javascript/lightGallery/dist/css/lightgallery.css">');

	$('#DeleteButton').click(function(){
		if (confirm('Do want to delete all images?') == true) {
			$.ajax({
				type: "GET",
				url: "/plugin/capture/capture.py/delete_captures",
				contentType: "application/json; charset=utf-8",
				success: function(response){
		        	if (response.Result == 'OK') {
		        		show_captures();
		        	}
		        	else {
		        		alert(response.Message)
		        	}
				}
			});
		}
		return false;
	});

    show_captures();
}


function show_captures() {
	// remove all images
	$("#GalleryContainer").empty();
	
	// show all available images
	$.ajax({
        type: "GET",
        url: "/plugin/capture/capture.py/get_captures",
        contentType: "application/json; charset=utf-8",
        success: function(response){
        	if (response.Result == 'OK') {
        		$(response.Captures).each(function () {
        			$("#GalleryContainer").append('<a href="/captures/' + this + '"><img src="/captures/' + this + '" width="100"/></a>');
        		});

        		$('#GalleryContainer').lightGallery();
        		
        		wait_for_new_captures();
        	}
        	else {
        		alert(response.Message)
        	}
        }
    });
}

function wait_for_new_captures() {
	$.ajax({
        type: "GET",
        url: "/plugin/capture/capture.py/wait_for_new_captures",
        contentType: "application/json; charset=utf-8",
        success: function(response){
        	if (response.Result == 'OK') {
        		$(response.Captures).each(function () {
        			$("#GalleryContainer").append('<a href="/captures/' + this + '"><img src="/captures/' + this + '" width="100"/></a>');
        		});
        		
        		$('#GalleryContainer').lightGallery(); //TODO: clarify why does this not work for new images
        		
        		wait_for_new_captures(); // continue recursively
        	}
        	else {
        		alert(response.Message)
        	}
        }
    });
}
