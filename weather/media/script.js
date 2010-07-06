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
	var val = $(row + " input[type='text']").val();
	if (val == "Default value is " + defVal) {
		$(row + " input[type='text']").css("color", "rgb(150, 150, 150)");

		$(row + " input[type='text']").click(function() {
			$(row + " input[type='text']").val("");
			$(row + " input[type='text']").css("color", "black");
		});
	}
}

// Hides the more info text and shows the more info link initially, and sets
// the ilnk to display the text upon click.
function swapText(infoSect) {
	$(infoSect + " .more-info-link").css("display", "inline");
	$(infoSect + " .more-info-text").css("display", "none");
	
	$(infoSect + " .more-info-link").click(function() {
		if ($(infoSect + " .more-info-link").text() == "(More detail)") {
			$(infoSect + " .more-info-text").css("display", "inline");
			$(infoSect + " .more-info-link").text("(Less detail)");
		} else {
			$(infoSect + " .more-info-text").css("display", "none");
			$(infoSect + " .more-info-link").text("(More detail)");
		}
	});
}

$(document).ready(function() {

	// Shows or hides sections based on the initial selection of checkboxes.
	// By, default (ie, with javascript turned off), all sections will be 
	// shown since they are only ever hidden here. Also, sets the sections
	// to expand/collapse upon click.
	showOrHideSect("input#node-down-check", "div#node-down-section");
	showOrHideSect("input##version-check", "div#version-section");
	showOrHideSect("input#band-low-check", "div#band-low-section");
	showOrHideSect("input#t-shirt-check", "div#t-shirt-section");

	// Turns the input field text gray and makes the text disappear on click
	// if it has the "Default Value is ---" when the page loads.
	showDefault("div#node-down-grace-pd-row", 1);
	showDefault("div#band-low-threshold-row", 20);

	// Initially hides the 'more info' text and displays a link, then sets
	// that link to display the text upon click (and hide itself). Without
	// javascript, the more info text will be shown and the link will be
	// hidden.
	swapText("span#node-down-more-info");
	swapText("span#version-more-info");
	swapText("span#band-low-more-info");
	swapText("span#t-shirt-more-info");

	$("span#more-info a").hover(function() {
		$("span#more-info-hover").toggle();
	});
});

