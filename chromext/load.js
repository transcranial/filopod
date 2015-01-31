$(function() {

	var DOMAIN = 'http://www.filopod.com';
	//var AJAX_URL = 'http://www.filopod.com/process_add_resource';
	var LOGIN_URL = 'http://www.filopod.com/accounts/login/';
	var MANAGE_URL = 'http://www.filopod.com/main/manage/';
	var EXPLORE_URL = 'http://www.filopod.com/main/exploration/';

	/*function getCookies(domain, name, callback) {
		chrome.cookies.get({"url": domain, "name": name}, function (cookie) {
			if (cookie) {
				callback(cookie.value);
			} else {
				callback('no cookie');
			}
		});
	}*/

	$('#manage').click(function () {
		chrome.tabs.create({ url: MANAGE_URL });
	});
	$('#explore').click(function () {
		chrome.tabs.create({ url: EXPLORE_URL });
	});

	/*$('#add').click(function () {
		$('#domain_select').hide();
		$('.cssbutton').slideUp();
		
		chrome.tabs.getSelected(null, function (tab) {
			chrome.tabs.sendRequest(tab.id, {action: "getHtml"}, function (response) {
				if (response.html) {
					//var text = document.createTextNode(response.html);
					//document.body.appendChild(text);
					$('#status').html('<center>Processing...<br><img src="ajax-loader.gif" align="middle"></center>');
					getCookies(DOMAIN, 'csrftoken', function (csrf_token) {
						if (csrf_token !== 'no cookie') { // has csrftoken cookie
							var csrfSafeMethod = function (method) {
								// these HTTP methods do not require CSRF protection
								return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
							}
							$.ajaxSetup({
								crossDomain: false,
								beforeSend: function(xhr, settings) {
									if (!csrfSafeMethod(settings.type)) {
										xhr.setRequestHeader("X-CSRFToken", csrf_token);
									}
								}
							});
							$.ajax({url: AJAX_URL,
								type: 'POST',
								data: { domain_name: $('#domain_select select').val(), html_url: tab.url, html_source: response.html},
								success: function(data) {
									$('#status').html('<center>Success! Sent to queue for computational analysis. Go to Manage Resources to monitor progress.<br>');
									$('#status').append('<img src="success.png" align="middle"></center>');
								},
								error: function(jqXHR, textStatus, errorThrown) {
									if (jqXHR.status == 401) { // redirects to login page
										chrome.tabs.create({ url: LOGIN_URL });
										$('#status').html('<center>Please sign in.<br><img src="login.png" align="middle"></center>');
									} else {
										$('#status').html('<center>Error encountered.<br><img src="error.png" align="middle"></center>');
									}
								}
							});
						} else { // redirects to login page
							chrome.tabs.create({ url: LOGIN_URL });
							$('#status').html('<center>Please sign in.<br><img src="login.png" align="middle"></center>');
						}
					});
				} else {
					$('#status').html('<center>Error encountered.<br><img src="error.png" align="middle"></center>');
				}
				
				$('#status').css('top', $(window).height() / 2 - 25);
				$('#status').css('left', ($(window).width() - $('#status').width()) / 2);
			});
		});
	});*/

});