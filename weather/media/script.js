// Shows or hides sections based on initial selection of checkboxes and future
// clicks of checkboxes.
function showOrHideSect(check, sect) {
	if ($(check).attr('checked')) {
		$(sect).show();
	} else {
		$(sect).hide();
	}

	$(check).click(function() {
		$(sect).toggle();
	});
}

// Turns the input field in row row gray and makes text disappear on click
// if it initially had "Default value is --def_val--".
function showDefault(row, defVal) {
	var box = $(row + " input[type='text']")

	if (box.val() === "") {
		box.val("Default value is " + defVal);
	}

	if (box.val() == "Default value is " + defVal) {
		box.css("color", "rgb(150, 150, 150)");

		box.click(function() {
			box.val("");
			box.css("color", "black");
		});
	}
}

$(document).ready(function() {

	// Shows or hides sections based on the initial selection of checkboxes.
	// By, default (ie, with javascript turned off), all sections will be 
	// shown since they are only ever hidden here. Also, sets the sections
	// to expand/collapse upon click.
	showOrHideSect("input#id_get_node_down", "div#node-down-section");
	showOrHideSect("input#id_get_version", "div#version-section");
	showOrHideSect("input#id_get_band_low", "div#band-low-section");
	showOrHideSect("input#id_get_t_shirt", "div#t-shirt-section");

	// Turns the input field text gray and makes the text disappear on click
	// if it has the "Default Value is ---" when the page loads.
	showDefault("div#node-down-section", 1);
	showDefault("div#band-low-section", 20);

	$("#more-info a").hover(function() {
		$("#more-info span").toggle();
	});

	$("div#search-container").show();
	setAutoComplete("router_search", "search-results", "/router_lookup/?query=");
	$("div#search-container").hide();

	$("#fingerprint-container a").show();
	$("#fingerprint-container a").toggle(function() {
		$(this).html('(hide fingerprint search)'); 
		$("div#search-container").show();
	}, function() {
		$(this).html('(search by router name)');
		$("div#search-container").hide();
	});
});

