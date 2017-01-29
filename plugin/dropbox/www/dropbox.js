window.plugin = {
  name: 'Dropbox',
  loaded: 'dropbox_plugin_loaded',
  onselect: 'dropbox_plugin_update'
};


function dropbox_plugin_loaded() {

    $('#DropboxGetAuthKeyButton').click(function(){
	    $.ajax({
	        type: "GET",
	        async: false, // avoid popup blocker
	        url: "/plugin/dropbox/dropbox.py/authurl",
	        contentType: "application/json; charset=utf-8",
	        success: function(response){
				if (response.Result == 'ERROR')
					alert(response.Message);
				else
	    			window.open(response.Url);
	        },
	    });
		return false;
    });

    $('#DropboxSubmitAuthKeyButton').click(function(){
	  	var dataString = 'code=' + $('#DropboxAuthCode').val();
		$.ajax({
			type: "POST",
			url: "/plugin/dropbox/dropbox.py/authorize",
			data: dataString,
			dataType: "json",
			success: function(response) {
				if (response.Result == 'OK') {
					//alert('Authorization done.');
					$('#DropboxAuthCode').val('');
					dropbox_plugin_update();
				}
				else
					alert(response.Message);
			},
			error: function (xhr, ajaxOptions, thrownError) {
	    		alert('Error: ' + xhr.status + ' - ' + thrownError);
	  		},
		});
		return false;
    });

    $('#DropboxDisconnectButton').click(function(){
    	if (confirm('Do you really want to disconnect?')) {
		    $.ajax({
		        type: "GET",
		        url: "/plugin/dropbox/dropbox.py/disconnect",
		        contentType: "application/json; charset=utf-8",
		        success: function(response){
		        	dropbox_plugin_update();
		        },
				error: function (xhr, ajaxOptions, thrownError) {
		    		alert('Error: ' + xhr.status + ' - ' + thrownError);
		  		},
		    });
		}
    });

    $('#DropboxDeleteFilesButton').click(function(){
    	if (confirm('Do you really want to delete all images?')) {
    		$("body").css("cursor", "progress");
		    $.ajax({
		        type: "GET",
		        url: "/plugin/dropbox/dropbox.py/delete_files",
		        contentType: "application/json; charset=utf-8",
		        success: function(response){
		        	dropbox_plugin_update();
					$("body").css("cursor", "default");
		        },
				error: function (xhr, ajaxOptions, thrownError) {
					$("body").css("cursor", "default");
		    		alert('Error: ' + xhr.status + ' - ' + thrownError);
		  		},
		    });
		}
    });
    
	$('#DropboxSaveButton').click(function(){

		var dataString = 'active=' + $("#DropboxUpload").prop('checked');
		$.ajax({
			type: "POST",
			url: "/plugin/dropbox/dropbox.py/set_config_data",
			data: dataString,
			dataType: "json",
			success: function(response) {
				if (response.Result == 'ERROR')
					alert(response.Message);
			},
			error: function (xhr, ajaxOptions, thrownError) {
				alert('Error: ' + xhr.status + ' - ' + thrownError);
			},
		});
		return false;
	});

	$('#DropboxCancelButton').click(function(){
		dropbox_plugin_update();
		return false;
	});

    dropbox_plugin_update();
}


function dropbox_plugin_update() {
    $.ajax({
        type: "GET",
        url: "/plugin/dropbox/dropbox.py/status",
        contentType: "application/json; charset=utf-8",
        success: function(response){
			$('#DropboxDisplayName').empty()
			$('#DropboxDisplayName').append(response.Info);
			if (response.Result == 'ERROR') {
				alert(response.Message);
			}
			else {
				if (response.IsConnected) {
					$('#DropboxFiles').empty()
					$('#DropboxFiles').append('Files: ' + response.Files);
					$('#DropboxRegContainer').hide();
					$('#DropboxDetails').show();
					$('#DropboxUnregContainer').show();
					if (response.Files == 0) {
						$('#DropboxDeleteFilesButton').prop("disabled", true);
					}
					else {
						$('#DropboxDeleteFilesButton').prop("disabled", false);
					}
				}
				else {
					$('#DropboxRegContainer').show();
					$('#DropboxDetails').hide();
					$('#DropboxUnregContainer').hide();
				}
			}
        }
    });
    
    $.ajax({
        type: "GET",
        url: "/plugin/dropbox/dropbox.py/get_upload_captures",
        contentType: "application/json; charset=utf-8",
        success: function(response){
			if (response.Result == 'ERROR') {
				alert(response.Message);
			}
			else {
	        	$("#DropboxUpload").prop('checked', (response.Active == true));
			}
        }
    });
}
