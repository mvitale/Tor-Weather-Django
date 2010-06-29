function showOrHide(check, sect) {
	if ($(check).attr('checked')) {
		$(sect).show();
	} else {
		$(sect).hide();
	}
}

$(document).ready(function() {

	showOrHide("#node-down-check input", "div#node-down-section");
	showOrHide("#out-of-date-check input", "div#out-of-date-section");
	showOrHide("#band-low-check input", "div#band-low-section");

	$("#node-down-check input").click(function() {
		$("div#node-down-section").slideToggle("fast");
	});
	$("#out-of-date-check input").click(function() {
		$("div#out-of-date-section").slideToggle("fast");
	});
	$("#band-low-check input").click(function() {
		$("div#band-low-section").slideToggle("fast");
	});
});

