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
	setAutoComplete("router_search", "search-results", "/router_name_lookup/?query=");
	$("div#search-container").hide();

	$("#fingerprint-container a").show();
	$("#fingerprint-container a").toggle(function() {
		$(this).html('(hide fingerprint search)'); 
		$("div#search-container").show();
	}, function() {
		$(this).html('(search by router name)');
		$("div#search-container").hide();
	});

	$("#router-search-submit").click(function() {
		var searchField = $("#search-container input");
		var searchLabel = $("#search-container label");
		var fingerprintField = $("#fingerprint-container input");
		var nonuniqueError = "Please enter the fingerprint manually if the router has a non-unique name";
		var noRouterError = "Please enter a valid router name:";
		var defaultLabel = "Enter router name, then click the arrow:";
		var t = setTimeout("searchLabel.css('font-weight', 'normal')", 500);

		$.getJSON("/router_fingerprint_lookup/?query=" + searchField.val(), function(json){
			if (json == "nonunique_name") {
				searchLabel.html(nonuniqueError);
				searchLabel.css("color", "red");
			} else if (json == "no_router") {
				searchLabel.html(noRouterError);
				if (searchLabel.css("color") == "red") {
					searchLabel.css("font-weight", "bold");
					t;
				} else {
					searchLabel.css("color", "red");
				}
			} else {
				fingerprintField.val(json);
				searchLabel.html(defaultLabel);
				searchLabel.css("color", "black");
			}
		});		
	});
});

