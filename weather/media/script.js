function showOrHide(check, sect) {
	if ($(check).attr('checked')) {
		$(sect).show();
	} else {
		$(sect).hide();
	}
}

function showDefault(row, def_val, min_val, max_val) {
	var val = $(row + " input[type='text']").val();
	if (val == "Default value is " + def_val ||
			$(row + " input[type='hidden']").val() == 'on') {
		$(row + " input[type='text']").css("color", "rgb(150, 150, 150)");

		$(row + " input[type='text']").click(function() {
			$(row + " input[type='text']").val("");
			$(row + " input[type='text']").css("color", "black");
		});
	}
}

$(document).ready(function() {

	showOrHide("#node-down-check input", "div#node-down-section");
	showOrHide("#version-check input", "div#version-section");
	showOrHide("#band-low-check input", "div#band-low-section");

	showDefault("div#node-down-grace-pd-row", 1, 1, 4500);
	showDefault("div#band-low-threshold-row", 20, 0, 100000);
	showDefault("div#band-low-grace-pd-row", 1, 1, 4500);

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

