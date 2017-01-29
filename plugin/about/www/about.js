window.plugin = {
  name: 'About',
  loaded: 'about_plugin_loaded'
};

function about_plugin_loaded() {

  	$.ajax({
		url: "/plugin/about/about.py",
		success: function(info) {
			$("#AboutInfo").text(info);
		},
	});
}
