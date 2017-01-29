window.plugin = {
  name: 'Settings',
  loaded: 'settings_plugin_loaded'
};

function settings_plugin_loaded() {

	// load multi-select jquery library async
	// $.getScript works sync and can not be used here!
	$.ajax({
        async: false,
        type: 'GET',
        url: '/javascript/multi-select/js/jquery.multi-select.js',
        dataType: 'script'
    });

	$('head').append('<link rel="stylesheet" type="text/css" href="/javascript/multi-select/css/multi-select.css">');

	$( "#SensitivitySlider" ).slider();
	
	$('#SettingsCancelButton').click(function(){
		getSettings();
		return false;
	});

	$('#SettingsSaveButton').click(function(){

		// determine active and inactive plugins
		var activePlugins = [];
		$('select#PluginSelect option:selected').each(function(index, element) {
		    activePlugins.push($(element).val());
		});
		var inactivePlugins = [];
		$('select#PluginSelect :not(option:selected)').each(function(index, element) {
		    inactivePlugins.push($(element).val());
		});
		
		if ($('#CameraWidth').val() > 1280) {
			alert('Invalid width parameter!');
			return false;
		}
		
		if ($('#CameraHeight').val() > 1280) {
			alert('Invalid height parameter!');
			return false;
		}
		
		$("body").css("cursor", "progress");
	  	var dataString = 'rotate=' + $('#CameraRotation').val()
	  		+ '&width=' + $('#CameraWidth').val()
	  		+ '&height=' + $('#CameraHeight').val()
	  		+ '&sensitivity=' + $('#SensitivitySlider').slider('option', 'value')
	  		+ '&activePlugins=' + activePlugins.join(',')
	  		+ '&inactivePlugins=' + inactivePlugins.join(',');
		$.ajax({
			type: "POST",
			url: "/plugin/settings/settings.py/set_settings",
			data: dataString,
			dataType: "json",
			success: function(response) {
				$("body").css("cursor", "default");
				if (response.Result == 'ERROR')
					alert(response.Message);
				else
					location.reload();
			},
			error: function (xhr, ajaxOptions, thrownError) {
				$("body").css("cursor", "default");
	    		alert('Error: ' + xhr.status + ' - ' + thrownError);
	  		},
		});
		return false;
	});

	getSettings();
}

function getSettings() {
    $.ajax({
        type: "GET",
        url: "/plugin/settings/settings.py/get_settings",
        contentType: "application/json; charset=utf-8",
        success: function(response){
			if (response.Result == 'ERROR')
				alert(response.Message);
			else {
	        	$("#CameraRotation").val(response.Rotate);
	        	$("#CameraWidth").val(response.Width);
	        	$("#CameraHeight").val(response.Height);
	        	$("#SensitivitySlider").slider("value", response.Sensitivity);
    		}
        },
    });
}

function createPluginsSelector() {
    $.ajax({
        type: "GET",
        url: "/plugin/settings/settings.py/get_plugins",
        contentType: "application/json; charset=utf-8",
        success: function(response){
			if (response.Result == 'ERROR')
				alert(response.Message);
			else {
				$('#PluginSelect').empty();
			    $(response.Plugins).each(function () {
			    	var optionSelected = '';
			    	var optionDisabled = '';
				    if (this['Active'] == true) {
				   		optionSelected = ' selected="selected"';
				   	}
			    	if (this['Optional'] == false) {
			    		optionDisabled = ' disabled="disabled"';
			    	}
				    $('#PluginSelect').append('<option value="' + this['Name'] + '"' + optionDisabled + optionSelected + '>' + pluginNames[this['Name']] + '</option>');
				});

				$('#PluginSelect').multiSelect( {
					keepOrder: false, 
					selectableHeader: "<div class='custom-header'>Available plugins</div>",
					selectionHeader: "<div class='custom-header'>Active plugins</div>"
				});
    		}
        },
    });
}

$(document).ready(function () {
	// must not be invoked before all plugins are loaded!
	createPluginsSelector();
});
