window.plugin = {
  name: 'Livecam',
  loaded: 'livecam_plugin_loaded',
  onselect: 'livecam_plugin_make_snapshot'
};


function livecam_plugin_loaded() {
	
	$('#SnapshotButton').click(function() {
		livecam_plugin_make_snapshot();
		return false;
	});

	livecam_plugin_make_snapshot();
}


function livecam_plugin_make_snapshot() {
    $.ajax({
        type: "GET",
        url: "/plugin/livecam/livecam.py/snapshot",
        contentType: "application/json; charset=utf-8",
        success: function(response){
			if (response.Result == 'ERROR')
				alert(response.Message);
			else {
    			$(".SnapshotImageContainer").empty();
    			$(".SnapshotImageContainer").append('<img src="' + response.Snapshot + '" alt="Snapshot" />');
    		}
        },
    });
}
