$(function () {
  // JavaScript to enable link to tab
    var url = document.location.toString();

    if (url.match('#')) {
	$('.nav-pills a[href=#' + url.split('#')[1] + ']').tab('show');
    }

  // Change hash for page-reload
    $('.nav-pills a').on('click', function (e) {
	window.location.hash = e.target.hash;
    });
});