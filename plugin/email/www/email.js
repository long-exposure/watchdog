window.plugin = {
  name: 'Email',
  loaded: 'email_plugin_loaded'
};


function email_plugin_loaded() {

	$('#EmailCancelButton').click(function(){
		getEmailData();
		return false;
	});

	$('#EmailSaveButton').click(function(){

		$("body").css("cursor", "progress");

		var dataString = 'active=' + $("#Active").prop('checked') +
		'&recipient=' + encodeURIComponent($('#Recipient').val()) +
		'&subject=' + encodeURIComponent($('#Subject').val()) +
		'&message=' + encodeURIComponent($('#Message').val()) +
		'&attach=' + $("#Attach").prop('checked') +
		'&smtp=' + encodeURIComponent($('#Smtp').val()) +
		'&user=' + encodeURIComponent($('#User').val()) +
		'&password=' + encodeURIComponent($('#Password').val());
		$.ajax({
			type: "POST",
			url: "/plugin/email/email.py/set_email_data",
			data: dataString,
			dataType: "json",
			success: function(response) {
				$("body").css("cursor", "default");
				if (response.Result == 'ERROR')
					alert(response.Message);
			},
			error: function (xhr, ajaxOptions, thrownError) {
				$("body").css("cursor", "default");
				alert('Error: ' + xhr.status + ' - ' + thrownError);
			},
		});
		return false;
	});

	getEmailData();
}


function getEmailData() {
    $.ajax({
        type: "GET",
        url: "/plugin/email/email.py/get_email_data",
        contentType: "application/json; charset=utf-8",
        success: function(response){
			if (response.Result == 'ERROR')
				alert(response.Message);
			else {
	        	$("#Active").prop('checked', (response.Active == 'true'));
	        	$("#Recipient").val(response.Recipient);
	        	$("#Subject").val(response.Subject);
	        	$("#Message").val(response.Message);
	        	$("#Attach").prop('checked', (response.Attach == 'true'));
	        	$("#Smtp").val(response.Smtp);
	        	$("#User").val(response.User);
	        	$("#Password").val(response.Password);
    		}
        },
    });
}
