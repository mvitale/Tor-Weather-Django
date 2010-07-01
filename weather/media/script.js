function showOrHide(check, sect) {
	if ($(check).attr('checked')) {
		$(sect).show();
	} else {
		$(sect).hide();
	}
}

function showDefault(row, def_val, min_val, max_val) {
	var val = $(row + " input[type='text']").val();
	if (val == "Default value is " + def_val) {
		$(row + " input[type='text']").css("color", "rgb(150, 150, 150)");

		$(row + " input[type='text']").click(function() {
			$(row + " input[type='text']").val("");
			$(row + " input[type='text']").css("color", "black");
		});
	}
}

$(document).ready(function() {

	showOrHide("input#node-down-check", "div#node-down-section");
	showOrHide("input##version-check", "div#version-section");
	showOrHide("input#band-low-check", "div#band-low-section");
	showOrHide("input#t-shirt-check", "div#t-shirt-section");

	showDefault("div#node-down-grace-pd-row", 1, 1, 4500);
	showDefault("div#band-low-threshold-row", 20, 0, 100000);
	showDefault("div#band-low-grace-pd-row", 1, 1, 4500);

	$("input#node-down-check").click(function() {
		$("div#node-down-section").toggle();
	});
	$("input#version-check").click(function() {
		$("div#version-section").toggle();
	});
	$("input#band-low-check").click(function() {
		$("div#band-low-section").toggle();
	});
	$("input#t-shirt-check").click(function() {
		$("div#t-shirt-section").toggle();
	});
});

