window.plugin = {
  name: 'Telegram',
  loaded: 'telegram_plugin_loaded'
};


function telegram_plugin_loaded() {

	$("head link[rel='stylesheet']").last().after("<link href='/plugin/telegram/telegram.css' rel='stylesheet' type='text/css'>");
	
    $("#TelegramRegInfoOpener").on("click", function() {
        $("#TelegramRegInfo").dialog("open");
    });

    $("#TelegramRegInfo").dialog({
        autoOpen: false,
        show: true,
        hide: true,
    });
    
    $('#TelegramVerboseCheckbox').click(function() {
    	if( $(this).is(':checked')) {
        	$("#TelegramInfoMessages").show();
        } else {
        	$("#TelegramInfoMessages").hide();
        }
    });
    
    $('#TelegramTokenButton').click(function(){
	  	var dataString = 'token=' + $('#TelegramTokenInput').val();
		$.ajax({
			type: "POST",
			url: "/plugin/telegram/telegram.py/save_token",
			data: dataString,
			dataType: "json",
			success: function(response) {
				if (response.Result == 'OK') {
					$('#TelegramTokenInput').val('');
					telegram_plugin_update();
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

    $('#TelegramDisconnectButton').click(function(){
    	if (confirm('Do you really want to disable your telegram bot?')) {
    		$("body").css("cursor", "progress");
		    $.ajax({
		        type: "GET",
		        url: "/plugin/telegram/telegram.py/disconnect",
		        contentType: "application/json; charset=utf-8",
		        success: function(response){
		        	telegram_plugin_update();
					$("body").css("cursor", "default");
		        },
				error: function (xhr, ajaxOptions, thrownError) {
					$("body").css("cursor", "default");
		    		alert('Error: ' + xhr.status + ' - ' + thrownError);
		  		},
		    });
		}
    });
       
	$('#TelegramSaveButton').click(function(){

		var dataString = 'send_images=' + $("#TelegramSendImagesCheckbox").prop('checked') +
		'&verbose=' + $("#TelegramVerboseCheckbox").prop('checked') +
		'&startup_message=' + encodeURIComponent($('#TelegramStartupMessage').val()) +
		'&shutdown_message=' + encodeURIComponent($('#TelegramShutdownMessage').val());
		$.ajax({
			type: "POST",
			url: "/plugin/telegram/telegram.py/set_config_data",
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

	$('#TelegramCancelButton').click(function(){
		telegram_plugin_update();
		return false;
	});

    $('#TelegramSubscribersJTable').jtable({
        actions: {
            listAction:   '/plugin/telegram/telegram.py/list_subscribers',
            deleteAction: '/plugin/telegram/telegram.py/delete_subscriber'
        },
        fields: {
            ChatId: {
                key: true,
                list: false
            },
            Name: {
                title: 'Subscriber',
            },
            Type: {
                title: 'Type',
            },
        }
    });
    
    // check for subscribe requests periodically
	setInterval(function() {
		$.ajax({
			type: "GET",
			url: "/plugin/telegram/telegram.py/check_subscribe",
			dataType: "json",
			success: function(response) {
				if (response.Result == 'OK') {
					if (response.Subscriber.Found) {
						if (confirm('Watchdog: Telegram message received.\n\n' + response.Subscriber.Name + ' wants to subscribe.\n\nDo you allow it?')) {
							if (confirm('Are you sure?')) {
								$.ajax({
							        type: "GET",
							        url: "/plugin/telegram/telegram.py/subscribe",
							        data: 'chat_id=' + response.Subscriber.ChatId,
							        contentType: "application/json; charset=utf-8",
									success: function(response) {
										telegram_plugin_update()
									},
							        error: function (xhr, ajaxOptions, thrownError) {
							        	alert('Error: subscribe: ' + xhr.status + ' - ' + thrownError);
									},
							    });
							}
						}
					}
				}
				else {
					alert(response.Message);
				}
			},
			error: function (xhr, ajaxOptions, thrownError) {
	    		alert('Error: check_subscribe: ' + xhr.status + ' - ' + thrownError);
	  		},
		});
	}, 5000);

    telegram_plugin_update();
}


function telegram_plugin_update() {
    $.ajax({
        type: "GET",
        url: "/plugin/telegram/telegram.py/status",
        contentType: "application/json; charset=utf-8",
        success: function(response){
			$('#TelegramDisplayName').text(response.Info);
			if (response.Result == 'ERROR') {
				alert(response.Message);
			}
			else {
				if (response.IsConnected) {
					$('#TelegramBotName').text(response.BotName);
		        	$("#TelegramSendImagesCheckbox").prop('checked', (response.SendImages == true));
		        	$("#TelegramVerboseCheckbox").prop('checked', (response.Verbose == true));
		        	if (response.Verbose)
						$('#TelegramInfoMessages').show();
		        	else
						$('#TelegramInfoMessages').hide();
		        	$("#TelegramStartupMessage").val(response.StartupMessage);
		        	$("#TelegramShutdownMessage").val(response.ShutdownMessage);
				    $('#TelegramSubscribersJTable').jtable('load');
					$('#TelegramRegContainer').hide();
					$('#TelegramDetails').show();
					$('#TelegramUnregContainer').show();
				}
				else {
					$('#TelegramRegContainer').show();
					$('#TelegramDetails').hide();
					$('#TelegramUnregContainer').hide();
				}
			}
        }
    });
}
