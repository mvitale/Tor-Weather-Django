function showOrHide(check, sect) {
	if ($(check).attr('checked')) {
		$(sect).show();
	} else {
		$(sect).hide();
	}
}

function showDefault(row, def_val, min_val, max_val) {
	var val = $(row + " input").val();
	if (!(val >= min_val && val <= max_val)) {
		$(row + " input").val("Default value is " + def_val);
		$(row + " input").css("color", "rgb(150, 150, 150)");
		$(row + " input").click(function() {
			$(row + " input").val("");
		});
		$(row + " input").click(function() {
			$(row + " input").css("color", "black");
		});
	}
}

$(document).ready(function() {

	showOrHide("#node-down-check input", "div#node-down-section");
	showOrHide("#version-check input", "div#version-section");
	showOrHide("#band-low-check input", "div#band-low-section");

	showDefault("div#band-low-threshold-row", 20, 0, 100000);
	showDefault("div#band-low-grace-pd-row", 1, 1, 4500);

	var val = $("div#node-down-grace-pd-row input").val();
	if (!(val >= 1 && val <= 4500)) {
		$("div#node-down-grace-pd-row input").val("Default value is 1");
		$("div#node-down-grace-pd-row input").css("color", "rgb(150, 150, 150)");
		$("div#node-down-grace-pd-row input").click(function() {
			$("div#node-down-grace-pd-row input").val("");
		});
		$("div#node-down-grace-pd-row input").click(function() {
			$("div#node-down-grace-pd-row input").css("color", "black");
		});
	
	}


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

