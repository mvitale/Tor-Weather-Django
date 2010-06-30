function showOrHide(check, sect) {
	if ($(check).attr('checked')) {
		$(sect).show();
	} else {
		$(sect).hide();
	}
}

$(document).ready(function() {

	showOrHide("#node-down-check input", "div#node-down-section");
	showOrHide("#version-check input", "div#version-section");
	showOrHide("#band-low-check input", "div#band-low-section");

	$("#node-down-check input").click(function() {
		$("div#node-down-section").toggle();
	});
	$("#version-check input").click(function() {
		$("div#version-section").toggle();
	});
	$("#band-low-check input").click(function() {
		$("div#band-low-section").toggle();
	});
});

