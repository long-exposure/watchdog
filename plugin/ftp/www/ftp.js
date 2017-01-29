window.plugin = {
  name: 'FTP',
  loaded: 'ftp_plugin_loaded'
};


function ftp_plugin_loaded() {

	$('#FtpCancelButton').click(function(){
		getFtpData();
		return false;
	});

	$('#FtpSaveButton').click(function(){

		$("body").css("cursor", "progress");

		$.ajax({
			type: "POST",
			url: "/plugin/ftp/ftp.py/set_ftp_data",
			data: _determineDataString(),
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

	$('#FtpTestButton').click(function(){

		$("body").css("cursor", "progress");

		$.ajax({
			type: "POST",
			url: "/plugin/ftp/ftp.py/test_ftp_access",
			data: _determineDataString(),
			dataType: "json",
			success: function(response) {
				$("body").css("cursor", "default");
				if (response.Result == 'ERROR')
					alert(response.Message);
				else
					alert(response.Message + '\n\n' + response.Files + ' files found in directory.');
			},
			error: function (xhr, ajaxOptions, thrownError) {
				$("body").css("cursor", "default");
				alert('Cannot test FTP access: ' + xhr.status + ' - ' + thrownError);
			},
		});
		return false;
	});

	$('#FtpClearDirButton').click(function(){

		if (confirm('Do you really want to delete all files in ' + $('#FtpDirectory').val() + '?')) {
			$("body").css("cursor", "progress");
			$.ajax({
				type: "POST",
				url: "/plugin/ftp/ftp.py/clear_directory",
				data: _determineDataString(),
				dataType: "json",
				success: function(response) {
					$("body").css("cursor", "default");
					alert(response.Message);
				},
				error: function (xhr, ajaxOptions, thrownError) {
					$("body").css("cursor", "default");
					alert('Cannot clear FTP directory: ' + xhr.status + ' - ' + thrownError);
				},
			});
		}
		return false;
	});

	getFtpData();
}


function getFtpData() {
    $.ajax({
        type: "GET",
        url: "/plugin/ftp/ftp.py/get_ftp_data",
        contentType: "application/json; charset=utf-8",
        success: function(response){
			if (response.Result == 'ERROR')
				alert(response.Message);
			else {
	        	$("#FtpActive").prop('checked', response.Active);
	        	$("#FtpHost").val(response.Host);
	        	$("#FtpUser").val(response.User);
	        	$("#FtpPassword").val(response.Password);
	        	$("#FtpDirectory").val(response.Directory);
    		}
        },
		error: function (xhr, ajaxOptions, thrownError) {
			alert('Cannot get FTP data: ' + xhr.status + ' - ' + thrownError);
		},
    });
}


function _determineDataString() {
	return 'active=' + $("#FtpActive").prop('checked') +
	'&host=' + encodeURIComponent($('#FtpHost').val()) +
	'&user=' + encodeURIComponent($('#FtpUser').val()) +
	'&password=' + encodeURIComponent($('#FtpPassword').val()) +
	'&directory=' + encodeURIComponent($('#FtpDirectory').val());
}
