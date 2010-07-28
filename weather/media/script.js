// Expands/collapses sections.
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

// Styles text boxes that say 'Default value is --defVal--'.
function showDefault(row, defVal) {
	var box = $(row + " input[type='text']")

	if (box.val() === "") {
		box.val("Default value is " + defVal);
	}

	if (box.val() === "Default value is " + defVal) {
		box.addClass("default-display");
	}

	if (box.hasClass("default-display")) {
		box.click(function() {
			box.val("");
			box.removeClass("default-display");
			box.addClass("nondefault-display");
		})
	}
}

$(document).ready(function() {
	// Expands/collapses sections.
	showOrHideSect("input#id_get_node_down", "div#node-down-section");
	showOrHideSect("input#id_get_version", "div#version-section");
	showOrHideSect("input#id_get_band_low", "div#band-low-section");
	showOrHideSect("input#id_get_t_shirt", "div#t-shirt-section");

	// Styles text boxes that say 'Default value is --defVal--'.
	showDefault("div#node-down-section", 1);
	showDefault("div#band-low-section", 20);

	// Show description about '(More Info)' link.
	$("#more-info a").hover(function() {
		$("#more-info span").toggle();
	});



	// Setup variables
	var fingerprintLink = $("#show-search-link");
	var searchContainer = $("div#search-container");
	var showLink = "(search by router name)";
	var hideLink = "(hide fingerprint search)";

	// Autocomplete setup, which seems to only work if the field is visible
	// when it's set up.
	searchContainer.show();
	setAutoComplete("router_search", "search-results", "/router_name_lookup/?query=");
	searchContainer.hide();

	// Expands/collapses search field area.
	fingerprintLink.show();
	fingerprintLink.toggle(function() {
		$(this).html(hideLink); 
		searchContainer.show();
	}, function() {
		$(this).html(showLink);
		searchContainer.hide();
	});

	$("#router_search").keypress(function(event) {
		if (event.keyCode == 13) {
			event.preventDefault();
			clearAutoComplete();
			$("#router-search-submit").click();
			return true;
		}
	});


	// Looks up fingerprint based on router name.
	$("#router-search-submit").click(function() {
		var searchField = $("#search-container input");
		var searchLabel = $("#search-container label");
		var fingerprintField = $("#fingerprint-container input");
		var nonuniqueError = "Non-unique name; enter fingerprint manually"
		var noRouterError = "Please enter a valid router name:";
		var defaultLabel = "Enter router name, then click the arrow:";

		$.getJSON("/router_fingerprint_lookup/?query=" + searchField.val(), function(json) {
			if (json == "nonunique_name") {
				fingerprintField.val("");
				searchLabel.html(nonuniqueError);
				searchLabel.addClass("form-error");
			} else if (json == "no_router") {
				searchLabel.html(noRouterError);
				fingerprintField.val("");
				searchLabel.addClass("form-error");
			} else {
				fingerprintField.val(json);
				searchLabel.html(defaultLabel);
				searchLabel.removeClass("form-error");
				fingerprintLink.click();
			}
		});
	});
});

